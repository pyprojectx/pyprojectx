"""Creates and manages isolated build environments."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

import uv

from pyprojectx.hash import calculate_hash
from pyprojectx.log import logger

PYTHON_EXE = "python.exe" if sys.platform == "win32" else "python3"
UV_EXE = uv.find_uv_bin()
ENV_VAR_RE = re.compile(r"(?P<var>\$\{(?P<name>[A-Z0-9_]+)})")
INSTALL_MARKERS_DIR = ".install-markers"
INSTALL_IN_PROGRESS = "installing"


class IsolatedVirtualEnv:
    """Encapsulates the location and installation of an isolated virtual environment."""

    def __init__(self, base_path: Path, name: str, requirements_config: dict, prerelease=None) -> None:
        """Construct an IsolatedVirtualEnv.

        :param base_path: The base path for all environments
        :param name: The name for the environment
        :param requirements_config: The requirements and post-install script to install in the environment
        """
        self._name = name
        self._base_path = base_path
        # Locates the venv. Derived from the *configured* requirements, so locking them to concrete
        # versions doesn't move the venv to a different directory.
        self._hash = requirements_config.get("hash", calculate_hash(requirements_config))
        self._requirements = requirements_config.get("requirements", [])
        # Records what is actually installed. Locked requirements differ from the configured ones, so
        # a pw.lock change has to trigger a reinstall even though the venv path is unchanged.
        self._install_hash = calculate_hash(
            {"requirements": self._requirements, "post-install": requirements_config.get("post-install")}
        )
        self._custom_dir = bool(requirements_config.get("dir"))
        self._path = Path(requirements_config["dir"]) if self._custom_dir else self._compose_path()
        self.prerelease = prerelease

    @property
    def name(self) -> str:
        """The name of the isolated environment."""
        return self._name

    @property
    def path(self) -> Path:
        """The location of the isolated environment."""
        return self._path

    @property
    def scripts_path(self) -> Optional[Path]:
        """The location of the venv's scripts directory."""
        return self._path / "Scripts" if sys.platform == "win32" else self._path / "bin"

    @property
    def uses_custom_dir(self) -> bool:
        """Whether the venv lives in a directory configured with 'dir' instead of a hash-based one."""
        return self._custom_dir

    @property
    def install_marker_path(self) -> Path:
        """The file recording which requirements were successfully installed in this venv.

        Kept next to the venvs rather than inside them, because a custom 'dir' can be the project's
        own virtualenv, which pyprojectx must not write into.
        """
        return (self._base_path / INSTALL_MARKERS_DIR / self._env_id()).absolute()

    @property
    def is_installed(self) -> bool:
        if not self.scripts_path.is_dir():
            return False
        marker_hash = self._read_install_marker()
        if marker_hash is None and not self._custom_dir:
            # Hash-based venv created before install markers existed: assume it is complete rather
            # than reinstalling everything on the first run after an upgrade.
            return True
        return marker_hash == self._install_hash

    def install(self, quiet=False, install_path=None, post_install=None) -> None:
        """Create the virtual environment and install requirements.

        :param quiet: suppress output
        :param install_path: the path to .pyprojectx
        :param post_install: optional callable to run once the requirements are installed; the venv is
            only marked as installed if it returns without raising
        """
        logger.debug("Installing IsolatedVirtualEnv in %s", self.path)
        # Flag the venv as incomplete up front, so an install that fails or is interrupted is retried
        # next run. A *missing* marker can't mean that: it is what venvs from older versions look like.
        self._mark_installing()
        recreate_venv = not (self._custom_dir and self.scripts_path.is_dir())
        if recreate_venv:
            cmd = [
                UV_EXE,
                "venv",
                str(self.path),
                "--prompt",
                f"px-{self.name}",
                "--python",
                f"{sys.version_info.major}.{sys.version_info.minor}",
            ]
            # Never --clear a custom dir: it may be the project's own virtualenv.
            if not self._custom_dir:
                cmd.append("--clear")
            if quiet:
                cmd.append("--quiet")
            logger.debug("Calling uv: %s", " ".join(cmd))
            subprocess.run(cmd, check=True, stdout=sys.stderr)
        self._install_requirements(quiet)
        if install_path and self.scripts_path.exists():
            self._copy_scripts(install_path, self.scripts_path)
        # Mark before post-install, not after: a post-install command may run in its own tool context
        # and re-enter installation for it. It has to find the venv installed, or it recurses forever.
        self.mark_installed()
        if post_install:
            self._run_post_install(post_install)

    def _run_post_install(self, post_install) -> None:
        completed = False
        try:
            post_install()
            completed = True
        finally:
            if not completed:
                # A failed post-install leaves an incomplete venv: flag it so the next run retries.
                # Deleting the marker would not do -- that is what a venv from an older version
                # looks like, and those are taken at face value.
                self._mark_installing()

    def _copy_scripts(self, install_path, scripts_dir):
        # make the scripts dir available in .pyprojectx/<tool context name>
        ctx_path = install_path / self.name
        try:
            ctx_path.unlink(missing_ok=True)
            ctx_path.symlink_to(scripts_dir, target_is_directory=True)
        except Exception:  # noqa: BLE001
            logger.debug("Could not create symlink to %s, copy instead.", scripts_dir)
        if sys.platform.startswith("win") or not ctx_path.is_symlink():
            if ctx_path.is_symlink():
                ctx_path.unlink()
            else:
                shutil.rmtree(ctx_path, ignore_errors=True)
            ctx_path.mkdir(exist_ok=True)
            for file in scripts_dir.iterdir():
                shutil.copy2(file, ctx_path)
            # powershell activation script breaks when copied
            activate_ps1 = ctx_path / "activate.ps1"
            if activate_ps1.exists():
                activate_ps1.unlink()
                with activate_ps1.open("w") as f:
                    f.write(f". '{(scripts_dir / 'activate.ps1').absolute()}'")

    def _install_requirements(self, quiet=False):
        if not self._requirements:
            logger.debug("No requirements to install in %s", self.path)
            return
        logger.info("Installing packages in isolated environment... (%s)", ", ".join(sorted(self._requirements)))
        requirements_file_regex = re.compile(r"^-r\s+(.+)$")
        file_requirements = [r for r in self._requirements if requirements_file_regex.match(r)]
        regular_requirements = [
            expand_env_variables(r) for r in self._requirements if not requirements_file_regex.match(r)
        ]
        requirements_string = "\n".join(regular_requirements)
        cmd = [UV_EXE, "pip", "install", "-r", "-", "--python", str(self.scripts_path / PYTHON_EXE)]
        cmd += [param for f in file_requirements for param in f.split()]
        if quiet:
            cmd.append("--quiet")
        if self.prerelease:
            cmd += ["--prerelease", self.prerelease]
        subprocess.run(cmd, input=requirements_string.encode("utf-8"), stdout=sys.stderr, check=True)

    def check_is_installable(self, requirement_specs, quiet=False):
        cmd = [UV_EXE, "pip", "install", "--python", str(self.scripts_path / PYTHON_EXE), "--dry-run"]
        if quiet:
            cmd.append("--quiet")
        cmd += requirement_specs
        subprocess.run(cmd, stdout=sys.stderr, check=True)

    def remove(self):
        """Remove the entire virtual environment."""
        logger.info("Removing isolated environment in %s", self.path)
        shutil.rmtree(self.path, ignore_errors=True)
        self.unmark_installed()

    def mark_installed(self) -> None:
        """Record that install (and post-install, if any) completed successfully."""
        self._write_install_marker(self._install_hash)

    def _mark_installing(self) -> None:
        self._write_install_marker(INSTALL_IN_PROGRESS)

    def _write_install_marker(self, content: str) -> None:
        marker = self.install_marker_path
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(content, encoding="utf-8")

    def unmark_installed(self) -> None:
        """Clear the install marker so the next run retries installation."""
        self.install_marker_path.unlink(missing_ok=True)

    def _read_install_marker(self) -> Optional[str]:
        marker = self.install_marker_path
        if not marker.is_file():
            return None
        return marker.read_text(encoding="utf-8").strip()

    def run(
        self, cmd: Union[str, list[str]], env: dict, cwd: Union[str, bytes, os.PathLike], stdout=None
    ) -> subprocess.CompletedProcess:
        """Run a command inside the virtual environment.

        :param cmd: The command string to run
        :param env: additional environment variables
        :param cwd: current working directory
        :param stdout: redirect stdout to this stream
        :return: The subprocess.CompletedProcess instance
        """
        logger.info("Running command in isolated venv %s: %s", self.name, cmd)
        logger.debug("Adding scripts path to PATH: %s", self.scripts_path.absolute())
        path = os.pathsep.join((str(self.scripts_path.absolute()), os.environ.get("PATH", os.defpath)))

        extra_environ = {"PATH": path}
        if isinstance(cmd, list):
            cmd[0] = shutil.which(cmd[0], path=path) or cmd[0]
            shell = False
        else:
            shell = True

        env = {**os.environ, **extra_environ, **env}
        logger.debug("Final command to run: %s", cmd)
        logger.debug("Environment for running command: %s", env)
        logger.debug("Cwd for running command: %s", cwd)
        return subprocess.run(cmd, env=env, shell=shell, check=True, cwd=cwd, stdout=stdout)

    def _env_id(self):
        return f"{self._name.lower()}-{self._hash}-py{sys.version_info.major}.{sys.version_info.minor}"

    def _compose_path(self):
        return (self._base_path / self._env_id()).absolute()


def expand_env_variables(line):
    for env_var, var_name in ENV_VAR_RE.findall(line):
        value = os.getenv(var_name)
        if not value:
            continue

        line = line.replace(env_var, value)

    return line
