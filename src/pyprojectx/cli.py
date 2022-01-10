import subprocess
import sys
from typing import Iterable, List, Optional, Union

from pyprojectx.config import Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.initializer.initializers import initialize
from pyprojectx.log import logger, set_verbosity
from pyprojectx.wrapper import pw


def main() -> None:
    _run(sys.argv)


def _run(argv: List[str]) -> None:
    options = _get_options(argv[1:])
    if options.init:
        initialize(options)
        return

    config = Config(options.toml_path)
    cmd = options.cmd
    if options.info:
        config.show_info(cmd)
        return

    aliases = config.find_aliases(cmd)
    logger.debug("Matching aliases for %s: %s", cmd, ", ".join(aliases))
    if aliases:
        if len(aliases) > 1:
            print(
                f"{pw.RED}'{cmd}' is ambiguous",
                file=sys.stderr,
            )
            print(
                f"{pw.BLUE}Candidates are:{pw.RESET}",
                file=sys.stderr,
            )
            print(", ".join(aliases), file=sys.stderr)
            raise SystemExit(1)
        tool, alias_cmd = config.get_alias(aliases[0])
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
        config.show_info(cmd, error=True)
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
    options = pw.get_options(args)
    if options.command:
        options.cmd, *options.cmd_args = options.command
    else:
        options.cmd = None
        options.cmd_args = []
    options.venvs_dir = options.install_path.joinpath("venvs")
    set_verbosity(options.verbosity)
    logger.debug("Parsed cli arguments: %s", options)
    return options
