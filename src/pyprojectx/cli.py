import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Union

from pyprojectx.config import Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.log import logger, set_verbosity
from pyprojectx.wrapper import pw


def main() -> None:
    _run(sys.argv)


def _run(argv: List[str]) -> None:
    options = _get_options(argv[1:])
    set_verbosity(options.verbosity)
    cmd = options.cmd
    config = Config(options.toml_path)
    tool, alias_cmd = config.get_alias(cmd)
    if alias_cmd:
        _run_alias(
            tool,
            alias_cmd,
            argv,
            requirements=config.get_tool_requirements(tool),
            options=options,
        )
    elif config.is_tool(cmd):
        _run_in_tool_venv(
            cmd,
            [cmd, *options.cmd_args],
            requirements=config.get_tool_requirements(cmd),
            options=options,
        )
    else:
        print(
            f"{pw.RED}'{cmd}' is not configured as pyprojectx tool or alias in {options.toml_path}{pw.RESET}",
            file=sys.stderr,
        )
        raise SystemExit(1)


def _run_alias(
    tool: Optional[str],
    alias_cmd: str,
    argv: List[str],
    requirements: Iterable[str],
    options,
) -> None:
    logger.debug("Running alias command, tool: %s, command: %s, arguments: %s", tool, alias_cmd, options.cmd_args)
    full_cmd = " ".join([_resolve_alias_references(alias_cmd, options.cmd, argv)] + options.cmd_args)
    if tool:
        _run_in_tool_venv(
            tool,
            full_cmd,
            requirements=requirements,
            options=options,
        )
    else:
        try:
            subprocess.run(full_cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise SystemExit(e.returncode) from e


def _run_in_tool_venv(
    tool: str,
    full_cmd: Union[str, List[str]],
    requirements: Iterable[str],
    options,
) -> None:
    logger.debug("Running tool command in virtual environment, tool: %s, full command: %s", tool, full_cmd)
    venv = IsolatedVirtualEnv(options.venvs_dir, tool, requirements)
    if not venv.is_installed or options.force_install:
        try:
            venv.install(quiet=options.quiet)
        except subprocess.CalledProcessError as e:
            print(
                f"{pw.RED}PYPROJECTX ERROR: installation of '{tool}' failed with exit code {e.returncode}{pw.RESET}",
                file=sys.stderr,
            )
            raise SystemExit(e.returncode) from e

    try:
        venv.run(full_cmd)
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode) from e


def _resolve_alias_references(alias_cmd: str, cmd: str, argv: List[str]) -> str:
    cmd_index = argv.index(cmd)
    replacement = " ".join(argv[:cmd_index]) + " "
    return alias_cmd.replace("pw@", replacement)


def _get_options(args):
    options = pw.arg_parser().parse_args(args)
    options.cmd = options.cmd[0]
    options.toml_path = Path(options.toml) if options.toml else Path(pw.PYPROJECT_TOML)
    options.install_path = Path(
        options.install_dir or os.environ.get(pw.PYPROJECTX_INSTALL_DIR_ENV_VAR, options.toml_path.parent)
    )
    options.venvs_dir = options.install_path.joinpath("venvs")
    options.verbosity = options.verbosity or 0
    if options.quiet:
        options.verbosity = 0
    logger.debug("Parsed cli arguments: %s", options)
    return options
