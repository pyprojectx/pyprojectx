import re
import sys
import tempfile
from pathlib import Path
from typing import Optional

import tomlkit

from pyprojectx.config import Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.hash import calculate_hash
from pyprojectx.wrapper import pw

EDITABLE_REGEX = re.compile(r"^--?e")


def get_locked_requirements(ctx_name: str, lock_file: Path) -> Optional[dict]:
    """Get the locked requirements for a context from the lock file.

    :param ctx_name: The name of the context
    :param lock_file: The path to the lock file
    :return: The locked requirements for the context
    """
    with lock_file.open() as f:
        toml = tomlkit.load(f)
    ctx = toml.get(ctx_name, {})
    return {"requirements": ctx.get("requirements"), "post-install": ctx.get("post-install"), "hash": ctx.get("hash")}


def can_lock(requirements_config: dict) -> bool:
    """Whether the requirements can be locked. If the requirements contain editable installs, they cannot be locked.

    :param requirements_config: requirements config dictionary
    :return: True if the requirements can be locked, False otherwise
    """
    return not any(EDITABLE_REGEX.search(req) for req in requirements_config.get("requirements", []))


def lock(config: Config, venvs_dir: Path, quiet, ctx_name=None) -> dict:
    """Lock the requirements for either a single context or all contexts.

    :param config: The config object
    :param venvs_dir: The path to the venvs directory
    :param quiet: Whether to suppress output
    :param ctx_name: The name of the context to lock. If None, lock all contexts.
    :return: The contents of the lock file as a dictionary.
    """
    lf = config.lock_file
    if not lf.exists():
        lf.touch()
    with lf.open() as f:
        toml = tomlkit.load(f)
    ctx_names = [ctx_name] if ctx_name else config.get_context_names()
    for ctx_name in ctx_names:
        requirements = config.get_requirements(ctx_name)
        if can_lock(requirements):
            _lock_ctx(ctx_name, requirements, toml, venvs_dir, quiet)
    with lf.open("w") as f:
        tomlkit.dump(toml, f)
    return toml


def _lock_ctx(ctx_name, requirements, toml, venvs_dir, quiet):
    if ctx_name not in toml:
        toml[ctx_name] = tomlkit.table()
    ctx = toml[ctx_name]
    locked_requirements = _freeze(ctx_name, requirements, venvs_dir, quiet)
    ctx["requirements"] = locked_requirements
    ctx["hash"] = calculate_hash(requirements)
    post_install = requirements.get("post-install")
    if post_install:
        ctx["post-install"] = post_install


def _freeze(ctx_name, requirements, venvs_dir, quiet):
    env = IsolatedVirtualEnv(venvs_dir, ctx_name, requirements)
    env.install(quiet)
    cmd = ["pip", "freeze", "--local"]
    if quiet:
        cmd.append("--quiet")
    else:
        print(f"{pw.BLUE}locking {pw.CYAN}{ctx_name}{pw.BLUE} requirements{pw.RESET}", file=sys.stderr)
    with tempfile.TemporaryFile() as fp:
        env.run(cmd, env={}, cwd=env.path, stdout=fp)
        fp.seek(0)
        return sorted([line.decode("utf-8").strip() for line in fp.readlines() if line])
