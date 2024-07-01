import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Union

from pyprojectx.config import MAIN, AliasCommand, Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.install_global import UPGRADE_INSTRUCTIONS, UPGRADE_INSTRUCTIONS_WIN, install_px
from pyprojectx.lock import can_lock, get_or_update_locked_requirements
from pyprojectx.log import logger, set_verbosity
from pyprojectx.requirements import add_requirement
from pyprojectx.wrapper import pw

alias_regex = re.compile(r"(pw)?@([\w-]+)")


def main() -> None:
    _run(sys.argv)


# ruff: noqa: PLR0911 C901
def _run(argv: list[str]) -> None:
    options = _get_options(argv[1:])
    if options.install_px:
        install_px(options)
        return

    if options.upgrade:
        _show_upgrade_instructions()
        return

    config = Config(options.toml_path)

    if options.add:
        add_requirement(options.add, options.toml_path, options.venvs_dir, options.quiet, config.prerelease)
        return

    if options.install_context:
        _install_ctx(options, config, argv)
        return

    if options.lock:
        _lock_requirements(argv, config, options)
        return

    cmd = options.cmd
    if options.info:
        config.show_info(cmd)
        return

    if options.clean:
        _clean_venvs(config, options)
        if not cmd:
            return

    if not cmd:
        pw.arg_parser().print_help(file=sys.stderr)
        raise SystemExit(1)

    cmd_index = argv.index(cmd)
    pw_args = argv[:cmd_index]
    if _run_alias_cmds(config, cmd, pw_args, options):
        return

    if _run_cmd_in_ctx(config, cmd, pw_args, options):
        return

    config.show_info(cmd, error=True)
    raise SystemExit(1)


def _run_alias_cmds(config, cmd, pw_args, options) -> bool:
    candidates = config.find_aliases_or_scripts(cmd)
    logger.debug("Matching aliases/scripts for %s: %s", cmd, ", ".join(candidates))
    if candidates:
        verify_ambiguity(candidates, cmd)
        alias_cmds = config.get_alias(candidates[0])
        if alias_cmds:
            for alias_cmd in alias_cmds:
                _run_alias(
                    alias_cmd,
                    pw_args,
                    options=options,
                    config=config,
                )
        else:
            _run_script(candidates[0], options, config)
        return True
    return False


def _run_cmd_in_ctx(config, cmd, pw_args, options) -> bool:
    ctx = config.get_ctx_or_main(cmd)
    if ctx:
        _run_in_ctx(
            ctx,
            [cmd, *options.cmd_args],
            options=options,
            pw_args=pw_args,
            config=config,
            env=config.env,
            cwd=config.get_cwd(),
        )
        return True
    return False


def verify_ambiguity(candidates, cmd):
    if len(candidates) > 1:
        print(
            f"{pw.RED}'{cmd}' is ambiguous",
            file=sys.stderr,
        )
        print(
            f"{pw.BLUE}Candidates are:{pw.RESET}",
            file=sys.stderr,
        )
        print(", ".join(candidates), file=sys.stderr)
        raise SystemExit(1)


def _run_alias(alias_cmd: AliasCommand, pw_args: list[str], options, config) -> None:
    logger.debug(
        "Running alias command, ctx: %s, command: %s, arguments: %s", alias_cmd.ctx, alias_cmd, options.cmd_args
    )
    quoted_args = [f'"{a}"' for a in options.cmd_args]
    full_cmd = " ".join([_resolve_references(alias_cmd.cmd, pw_args, config), *quoted_args])
    if alias_cmd.shell:
        full_cmd = [alias_cmd.shell, "-c", full_cmd]

    alias_env = {**config.env, **alias_cmd.env}
    if alias_cmd.ctx:
        _run_in_ctx(
            alias_cmd.ctx,
            full_cmd,
            options=options,
            pw_args=pw_args,
            config=config,
            env=alias_env,
            cwd=alias_cmd.cwd,
        )
    else:
        try:
            logger.debug(
                "Running command without venv, full command: %s, in %s, with shell %s",
                full_cmd,
                alias_cmd.cwd,
                alias_cmd.shell,
            )
            subprocess.run(full_cmd, shell=True, check=True, env={**os.environ, **alias_env}, cwd=alias_cmd.cwd)
        except subprocess.CalledProcessError as e:
            raise SystemExit(e.returncode) from e


def _run_script(script: str, options, config) -> None:
    file = config.get_script_path(script)
    logger.debug("Running script: %s, arguments: %s", file, options.cmd_args)
    full_cmd = ["python", file, *options.cmd_args]
    if config.is_ctx(MAIN):
        _run_in_ctx(
            MAIN,
            full_cmd,
            options=options,
            pw_args=[],
            config=config,
            env=config.env,
            cwd=config.cwd,
        )
    else:
        try:
            logger.debug("Running script without venv, full command: %s, in %s", full_cmd, config.cwd)
            subprocess.run(full_cmd, shell=True, check=True, env={**os.environ, **config.env}, cwd=config.cwd)
        except subprocess.CalledProcessError as e:
            raise SystemExit(e.returncode) from e


# ruff: noqa: PLR0913
def _run_in_ctx(ctx: str, full_cmd: Union[str, list[str]], options, pw_args, config, env, cwd) -> None:
    logger.debug("Running command in virtual environment, ctx: %s, full command: %s", ctx, full_cmd)
    venv = _ensure_ctx(config, ctx, env, options, pw_args)
    try:
        venv.run(full_cmd, env, cwd)
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode) from e


def _ensure_ctx(config, ctx, env, options, pw_args):
    requirements, modified = get_or_update_locked_requirements(ctx, config, options.quiet)
    venv = IsolatedVirtualEnv(options.venvs_dir, ctx, requirements, prerelease=config.prerelease)
    if not venv.is_installed or options.force_install or modified:
        try:
            venv.install(quiet=options.quiet, install_path=options.install_path)
            if requirements.get("post-install"):
                post_install_cmd = _resolve_references(requirements["post-install"], pw_args, config=config)
                venv.run(post_install_cmd, env, config.get_cwd())
        except subprocess.CalledProcessError as e:
            print(
                f"{pw.RED}PYPROJECTX ERROR: installation of '{ctx}' failed with exit code {e.returncode}{pw.RESET}",
                file=sys.stderr,
            )
            raise SystemExit(e.returncode) from e
    return venv


def _resolve_references(alias_cmd: str, pw_args: list[str], config) -> str:
    """Resolve all @alias and pw@ references."""
    alias_refs = alias_regex.findall(alias_cmd)
    for optional_pw, alias in alias_refs:
        if config.is_alias(alias) or config.get_script_path(alias).exists():
            alias_cmd = alias_cmd.replace(f"{optional_pw}@{alias}", f"pw@{alias}")
    is_path = True
    skip = False
    absolute_pw_args = []
    for arg in pw_args:
        if arg in ["-t", "--toml", "-i", "--install-dir"]:
            is_path = True
            absolute_pw_args.append(arg)
        elif arg in ["--install-context"]:
            skip = True
        elif is_path:
            absolute_pw_args.append(str(Path(arg).absolute()))
            is_path = False
        elif skip:
            skip = False
        else:
            absolute_pw_args.append(arg)
    replacement = " ".join([_quote(arg) for arg in absolute_pw_args]) + " "
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
    options.venvs_dir = options.install_path / "venvs"
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
    print(
        f"{pw.BLUE}If you installed {pw.CYAN}px{pw.BLUE}, you can download the latest pw scripts "
        f"to the current directory by executing:{pw.RESET}\npxg download-pw",
    )


def _install_ctx(options, config, pw_args):
    ctx = options.install_context
    if not config.is_ctx(ctx):
        raise Warning(f"Invalid ctx: '{options.install_context}' is not defined in [tool.pyprojectx]")
    _ensure_ctx(
        config,
        ctx,
        options=options,
        pw_args=pw_args,
        env={},
    )


def _lock_requirements(argv, config, options):
    config.lock_file.unlink(missing_ok=True)
    config.lock_file.touch()
    argv.remove("--lock")
    for ctx in config.get_context_names():
        if can_lock(config.get_requirements(ctx)):
            if options.force_install:
                IsolatedVirtualEnv(options.venvs_dir, ctx, config.get_requirements(ctx)).remove()
            _ensure_ctx(config, ctx, env=config.env, options=options, pw_args=argv)


def _clean_venvs(config, options):
    pyprojectx_dir = options.install_path / "pyprojectx"
    pyprojectx_venv_dir = pyprojectx_dir / f"{options.version}-py{sys.version_info.major}.{sys.version_info.minor}"

    for f in pyprojectx_dir.glob("*"):
        if f.is_dir() and f.resolve() != pyprojectx_venv_dir.resolve():
            if not options.quiet:
                print(f"{pw.CYAN}Removing {pw.BLUE}{f.resolve()}{pw.RESET}", file=sys.stderr)
            shutil.rmtree(f, ignore_errors=True)

    ctxt_venvs = []
    for ctx in config.get_context_names():
        requirements, _ = get_or_update_locked_requirements(ctx, config, options.quiet)
        venv = IsolatedVirtualEnv(options.venvs_dir, ctx, requirements)
        ctxt_venvs.append(venv.path.resolve())
    for f in options.venvs_dir.glob("*"):
        if f.is_dir() and f.resolve() not in ctxt_venvs:
            if not options.quiet:
                print(f"{pw.CYAN}Removing {pw.BLUE}{f.resolve()}{pw.RESET}", file=sys.stderr)
            shutil.rmtree(f, ignore_errors=True)
