"""
Creates and manages isolated build environments.
"""
import hashlib
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict
from pathlib import Path
from subprocess import CompletedProcess
from typing import Dict, Iterable, List, Optional, Union

import virtualenv

_logger = logging.getLogger("build.env")

# TODO: debug logging with --px-verbose


def _log(message: str) -> None:
    if sys.version_info >= (3, 8):
        # TODO stacklevel: used in logging helpers so that the function name,
        #  filename and line number recorded are not the information for the helper function/method,
        #  but rather its caller
        _logger.log(logging.INFO, message, stacklevel=2)
    else:
        _logger.log(logging.INFO, message)


def _subprocess(cmd: List[str]) -> None:
    """
    Invoke subprocess and output stdout and stderr if it fails.
    """
    # TODO: necessary? maybe inline in IsolatedVirtualEnv.install
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(e.output.decode(), end="", file=sys.stderr)
        raise e


def _calculate_path(base_path: Path, name: str, requirements: Iterable[str]) -> Path:
    md5 = hashlib.md5()
    for req in requirements:
        md5.update(req.strip().encode())
    return Path(
        base_path, f"{name.lower()}-{sys.version_info.major}.{sys.version_info.minor}-{md5.hexdigest()}"
    ).absolute()


class IsolatedVirtualEnv:
    """
    Encapsulates the location and installation of an isolated virtual environment.
    """

    def __init__(self, base_path: Path, name: str, requirements: Iterable[str]) -> None:
        """
        :param base_path: The base path for all environments
        :param name: The name for the environment
        :param requirements: The requirements to install in the environment
        """
        self._base_path = base_path
        self._requirements = requirements
        self._path = _calculate_path(base_path, name, self._requirements)
        self._scripts_path_file = self._path.joinpath(".scripts_path")
        self._executable = None

    @property
    def path(self) -> Path:
        """
        The location of the isolated environment.
        """
        return self._path

    @property
    def executable(self) -> Optional[Path]:
        """
        The location of the Python executable of the isolated environment.
        """
        return self._executable

    @property
    def scripts_path(self) -> Optional[Path]:
        """
        The location of the scripts directory.
        """
        if self._scripts_path_file.exists():
            with open(self._scripts_path_file, "r") as sf:
                return Path(sf.readline())
        return None

    @property
    def is_installed(self) -> bool:
        return self.scripts_path and self.scripts_path.is_dir()

    def install(self) -> None:
        """
        Create the virtual environment and install requirements
        """
        scripts_dir = self._create_virtual_env()
        self._install_requirements()
        with open(self._scripts_path_file, "w") as sf:
            sf.write(str(scripts_dir))

    def _create_virtual_env(self) -> Path:
        cmd = [str(self.path), "--no-setuptools", "--no-wheel", "--activators", ""]
        result = virtualenv.cli_run(cmd, setup_logging=False)
        scripts_dir = result.creator.script_dir
        self._executable = result.creator.exe
        return scripts_dir

    def _install_requirements(self):
        _log("Installing packages in isolated environment... ({})".format(", ".join(sorted(self._requirements))))
        # pip does not honour environment markers in command line arguments
        # but it does for requirements from a file
        with tempfile.NamedTemporaryFile("w+", prefix="build-reqs-", suffix=".txt", delete=False) as req_file:
            req_file.write(os.linesep.join(self._requirements))
        try:
            cmd = [
                self._executable,
                "-Im",
                "pip",
                "install",
                "--use-pep517",
                "--no-warn-script-location",
                "-r",
                os.path.abspath(req_file.name),
            ]
            _subprocess(cmd)
        finally:
            os.remove(req_file.name)

    def remove(self):
        """
        Remove the entire virtual environment
        """
        shutil.rmtree(self.path)

    def run(self, cmd: Union[str, List[str]], capture_output=False) -> CompletedProcess:
        """
        Run a command inside the virual environment.
        :param cmd: The command string to run
        :param capture_output: Set to True if you want to capture the output of the command. Default is False.
        :return: The subprocess.CompletedProcess instance
        """
        paths: Dict[str, None] = OrderedDict()
        paths[str(self.scripts_path)] = None
        if "PATH" in os.environ:
            paths.update((i, None) for i in os.environ["PATH"].split(os.pathsep))
        extra_environ = {"PATH": os.pathsep.join(paths)}

        env = os.environ.copy()
        env.update(extra_environ)
        return subprocess.run(cmd, env=env, shell=isinstance(cmd, str), check=True, capture_output=capture_output)


__all__ = "IsolatedVirtualEnv"
