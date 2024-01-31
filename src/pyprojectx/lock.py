import re
import sys
import tempfile
from pathlib import Path
from typing import Tuple

import tomlkit

from pyprojectx.config import Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.hash import calculate_hash
from pyprojectx.wrapper import pw

EDITABLE_REGEX = re.compile(r"^--?e")


def can_lock(requirements_config: dict) -> bool:
    """Whether the requirements can be locked. If the requirements contain editable installs, they cannot be locked.

    :param requirements_config: requirements config dictionary
    :return: True if the requirements can be locked, False otherwise
    """
    return not requirements_config.get("dir") and not any(
        EDITABLE_REGEX.search(req) for req in requirements_config.get("requirements", [])
    )


def get_or_update_locked_requirements(ctx: str, config: Config, venvs_dir: Path, quiet) -> Tuple[dict, bool]:
    """Check if the locked requirements are up-to-date and lock them if needed.

    :param ctx: The context name to lock
    :param config: The config object
    :param venvs_dir: The path to the venvs directory
    :param quiet: Whether to suppress output
    :return: A tuple with the contents of the requirements dictionary and a bool whether the requirements were updated.
    """
    requirements = config.get_requirements(ctx)
    lf = config.lock_file

    if not lf.exists() or not can_lock(requirements):
        return requirements, False

    with lf.open() as f:
        toml = tomlkit.load(f)

    if ctx not in toml:
        toml[ctx] = tomlkit.table()
    toml_ctx = toml[ctx]
    requirements_hash = calculate_hash(requirements)
    if toml_ctx.get("hash") == requirements_hash:
        return toml_ctx, False

    locked_requirements = _freeze(ctx, requirements, venvs_dir, quiet)
    toml_ctx["requirements"] = locked_requirements
    toml_ctx["hash"] = requirements_hash
    post_install = requirements.get("post-install")
    if post_install:
        toml_ctx["post-install"] = post_install
    with lf.open("w") as f:
        tomlkit.dump(toml, f)
    return toml_ctx, True


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
