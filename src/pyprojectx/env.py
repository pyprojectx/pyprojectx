# ruff: noqa: S324
"""Creates and manages isolated build environments."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Union

import virtualenv

from pyprojectx.hash import calculate_hash
from pyprojectx.log import logger


class IsolatedVirtualEnv:
    """Encapsulates the location and installation of an isolated virtual environment."""

    def __init__(self, base_path: Path, name: str, requirements_config: dict) -> None:
        """Construct an IsolatedVirtualEnv.

        :param base_path: The base path for all environments
        :param name: The name for the environment
        :param requirements_config: The requirements and post-install script to install in the environment
        """
        self._name = name
        self._base_path = base_path
        self._hash = calculate_hash(requirements_config)
        self._requirements = requirements_config.get("requirements", [])
        self._path = self._compose_path()
        self._scripts_path_file = self._path.joinpath(".scripts_path")
        self._executable = None

    @property
    def name(self) -> str:
        """The name of the isolated environment."""
        return self._name

    @property
    def path(self) -> Path:
        """The location of the isolated environment."""
        return self._path

    @property
    def executable(self) -> Optional[Path]:
        """The location of the Python executable of the isolated environment."""
        return self._executable

    @property
    def scripts_path(self) -> Optional[Path]:
        """The location of the venv's scripts directory."""
        if self._scripts_path_file.exists():
            with self._scripts_path_file.open() as sf:
                return Path(sf.readline())
        return None

    @property
    def is_installed(self) -> bool:
        return self.scripts_path and self.scripts_path.is_dir()

    def install(self, quiet=False) -> None:
        """Create the virtual environment and install requirements."""
        logger.debug("Installing IsolatedVirtualEnv in %s", self.path)
        scripts_dir = self._create_virtual_env()
        self._install_requirements(quiet)
        with self._scripts_path_file.open("w") as sf:
            sf.write(str(scripts_dir))

    def _create_virtual_env(self) -> Path:
        cmd = [str(self.path), "--no-setuptools", "--no-wheel", "--activators", ""]
        logger.debug("Calling virtualenv.cli_run: %s", " ".join(cmd))
        result = virtualenv.cli_run(cmd, setup_logging=False)
        scripts_dir = result.creator.script_dir
        self._executable = result.creator.exe
        return scripts_dir

    def _install_requirements(self, quiet=False):
        logger.info("Installing packages in isolated environment... (%s)", ", ".join(sorted(self._requirements)))
        # pip does not honour environment markers in command line arguments,
        # but it does for requirements from a file
        with tempfile.NamedTemporaryFile("w+", prefix="build-reqs-", suffix=".txt", delete=False) as req_file:
            req_file.write(os.linesep.join(self._requirements))
        try:
            cmd = [
                str(self._executable),
                "-Im",
                "pip",
                "install",
            ]
            if quiet:
                cmd.append("--quiet")
            cmd += [
                "--use-pep517",
                "--no-warn-script-location",
                "-r",
                Path(req_file.name).resolve(),
            ]

            subprocess.run(
                cmd,
                stdout=sys.stderr,
                check=True,
            )
        finally:
            Path(req_file.name).unlink()

    def remove(self):
        """Remove the entire virtual environment."""
        logger.info("Removing isolated environment in %s", self.path)
        shutil.rmtree(self.path)

    def run(
        self, cmd: Union[str, List[str]], env: dict, cwd: Union[str, bytes, os.PathLike], stdout=None
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
        if isinstance(cmd, List):
            cmd[0] = shutil.which(cmd[0], path=path) or cmd[0]
            shell = False
        else:
            shell = True

        env = {**os.environ, **extra_environ, **env}
        logger.debug("Final command to run: %s", cmd)
        logger.debug("Environment for running command: %s", env)
        logger.debug("Cwd for running command: %s", cwd)
        return subprocess.run(cmd, env=env, shell=shell, check=True, cwd=cwd, stdout=stdout)

    def _compose_path(self):
        return Path(
            self._base_path,
            f"{self._name.lower()}-{self._hash}-py{sys.version_info.major}.{sys.version_info.minor}",
        ).absolute()
