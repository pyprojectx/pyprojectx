import os
import re
import subprocess
import sys
from typing import List, Union

from pyprojectx.config import AliasCommand, Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.initializer.initializers import initialize
from pyprojectx.log import logger, set_verbosity
from pyprojectx.wrapper import pw

UPGRADE_INSTRUCTIONS = (
    "curl -LO https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip"
    " && unzip -o wrappers.zip && rm -f wrappers.zip"
)
UPGRADE_INSTRUCTIONS_WIN = (
    "Invoke-WebRequest"
    " https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip"
    " -OutFile wrappers.zip; Expand-Archive -Force -Path wrappers.zip -DestinationPath .;"
    " Remove-Item -Path wrappers.zip"
)

alias_regex = re.compile(r"(pw)?@([\w-]+)")


def main() -> None:
    _run(sys.argv)


def _run(argv: List[str]) -> None:
    options = _get_options(argv[1:])
    if options.init:
        initialize(options)
        return

    if options.upgrade:
        _show_upgrade_instructions()
        return

    config = Config(options.toml_path)
    cmd = options.cmd
    if options.info:
        config.show_info(cmd)
        return

    if not cmd:
        pw.arg_parser().print_help(file=sys.stderr)
        raise SystemExit(1)

    cmd_index = argv.index(cmd)
    pw_args = argv[:cmd_index]
    aliases = config.find_aliases(cmd)
    logger.debug("Matching aliases for %s: %s", cmd, ", ".join(aliases))
    if aliases:
        verify_ambiguity(aliases, cmd)
        alias_cmds = config.get_alias(aliases[0])
        if alias_cmds:
            for alias_cmd in alias_cmds:
                _run_alias(
                    alias_cmd,
                    pw_args,
                    requirements=config.get_tool_requirements(alias_cmd.tool),
                    options=options,
                    config=config,
                )
    elif config.is_tool(cmd):
        _run_in_tool_venv(
            cmd,
            [cmd, *options.cmd_args],
            requirements=config.get_tool_requirements(cmd),
            options=options,
            pw_args=pw_args,
            config=config,
            env=config.env,
        )
    else:
        config.show_info(cmd, error=True)
        raise SystemExit(1)


def verify_ambiguity(aliases, cmd):
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


def _run_alias(alias_cmd: AliasCommand, pw_args: List[str], requirements: dict, options, config) -> None:
    logger.debug(
        "Running alias command, tool: %s, command: %s, arguments: %s", alias_cmd.tool, alias_cmd, options.cmd_args
    )
    quoted_args = [f'"{a}"' for a in options.cmd_args]
    full_cmd = " ".join([_resolve_references(alias_cmd.cmd, pw_args, config), *quoted_args])

    alias_env = {**config.env, **alias_cmd.env}
    if alias_cmd.tool:
        _run_in_tool_venv(
            alias_cmd.tool,
            full_cmd,
            requirements=requirements,
            options=options,
            pw_args=pw_args,
            config=config,
            env=alias_env,
        )
    else:
        try:
            subprocess.run(full_cmd, shell=True, check=True, env={**os.environ, **alias_env})
        except subprocess.CalledProcessError as e:
            raise SystemExit(e.returncode) from e


# ruff: noqa: PLR0913
def _run_in_tool_venv(
    tool: str, full_cmd: Union[str, List[str]], requirements: dict, options, pw_args, config, env
) -> None:
    logger.debug("Running tool command in virtual environment, tool: %s, full command: %s", tool, full_cmd)
    venv = IsolatedVirtualEnv(options.venvs_dir, tool, requirements)
    if not venv.is_installed or options.force_install:
        try:
            venv.install(quiet=options.quiet)
            if requirements["post-install"]:
                post_install_cmd = _resolve_references(requirements["post-install"], pw_args, config=config)
                venv.run(post_install_cmd, env)
        except subprocess.CalledProcessError as e:
            print(
                f"{pw.RED}PYPROJECTX ERROR: installation of '{tool}' failed with exit code {e.returncode}{pw.RESET}",
                file=sys.stderr,
            )
            raise SystemExit(e.returncode) from e

    try:
        venv.run(full_cmd, env)
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode) from e


def _resolve_references(alias_cmd: str, pw_args: List[str], config) -> str:
    """Resolve all @alias and pw@ references."""
    alias_refs = alias_regex.findall(alias_cmd)
    for optional_pw, alias in alias_refs:
        if config.is_alias(alias):
            alias_cmd = alias_cmd.replace(f"{optional_pw}@{alias}", f"pw@{alias}")
    replacement = " ".join([_quote(arg) for arg in pw_args]) + " "
    return alias_cmd.replace("pw@", replacement)


def _quote(arg):
    if " " in arg:
        return f'"{arg}"'
    return arg


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


def _show_upgrade_instructions():
    print(
        f"{pw.BLUE}Upgrade to the latest version of Pyprojectx by executing following command in a terminal:{pw.RESET}",
    )
    if sys.platform.startswith("win"):
        print(UPGRADE_INSTRUCTIONS_WIN)
    else:
        print(UPGRADE_INSTRUCTIONS)
