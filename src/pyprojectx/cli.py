import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Union

from pyprojectx.config import Config
from pyprojectx.env import IsolatedVirtualEnv


def main():
    options = _parse_args()
    cmd = options.cmd[0]
    px_home = Path(options.px_home or os.environ.get("PYPROJECTX_HOME", Path.home().joinpath(".pyprojectx")))
    config = Config(Path(options.config))
    tool, alias_cmd = config.get_alias(cmd)
    if alias_cmd:
        _run_alias(
            tool,
            alias_cmd,
            options.cmd_args,
            requirements=config.get_tool_requirements(tool),
            px_home=px_home,
            px_wrapper=options.px_wrapper,
            force_install=options.force_install,
        )
    elif config.is_tool(cmd):
        _run_in_tool_venv(
            cmd,
            [cmd, *options.cmd_args],
            requirements=config.get_tool_requirements(cmd),
            px_home=px_home,
            force_install=options.force_install,
        )
    else:
        print(f"'{cmd}' is not configured as pyprojectx tool or alias in {options.config}", file=sys.stderr)
        raise SystemExit(1)


def _run_alias(
    tool: Optional[str],
    alias_cmd: str,
    cmd_args: List[str],
    requirements: Iterable[str],
    px_home: Path,
    px_wrapper: str = "./pw",
    force_install=False,
):
    full_cmd = " ".join([alias_cmd.replace("./pw", px_wrapper)] + cmd_args)
    if tool:
        _run_in_tool_venv(
            tool,
            full_cmd,
            requirements=requirements,
            px_home=px_home,
            force_install=force_install,
        )
    else:
        subprocess.run(full_cmd, shell=True, check=True)


def _run_in_tool_venv(
    tool: str,
    full_cmd: Union[str, List[str]],
    requirements: Iterable[str],
    px_home: Path,
    force_install=False,
):
    venv = IsolatedVirtualEnv(px_home.joinpath("venvs"), tool, requirements)
    if not venv.is_installed or force_install:
        venv.install()
    venv.run(full_cmd)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Execute commands or aliases defined in the [tool.pyprojectx] section of pyproject.toml",
    )
    parser.add_argument("--version", action="version", version="TODO")  # TODO
    parser.add_argument(
        "--config",
        "-c",
        metavar="config.toml",
        action="store",
        default="pyproject.toml",
        help="the toml config file (default: ./pyproject.toml)",
    )
    parser.add_argument(
        "--px-home",
        metavar="pyprojectx-home-dir",
        action="store",
        help="the directory where virtual environments are created and cached "
        + "(default: PYPROJECTX_HOME environment value if set, else {user-home}/.pyprojectx)",
    )
    parser.add_argument(
        "--px-wrapper", metavar="pw-script", action="store", default="./pw", help="the pyprojectx wrapper script"
    )
    parser.add_argument(
        "--force-install",
        "-f",
        action="store_true",
        help="force clean installation of the virtual environment used to run the command, if any",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="show debug output",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="show debug output",
    )
    parser.add_argument("cmd", nargs=1, help="the command or alias to execute")
    parser.add_argument("cmd_args", nargs=argparse.REMAINDER, help="the arguments for the command or alias")

    return parser.parse_args()
