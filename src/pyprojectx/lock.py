import re
import subprocess
import sys

import tomlkit

from pyprojectx.config import Config
from pyprojectx.env import UV_EXE
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


def get_or_update_locked_requirements(ctx: str, config: Config, quiet) -> tuple[dict, bool]:
    """Check if the locked requirements are up-to-date and lock them if needed.

    :param ctx: The context name to lock
    :param config: The config object
    :param quiet: Whether to suppress output
    :return: A tuple with the contents of the requirements dictionary and a bool whether the requirements were updated.
    """
    requirements = config.get_requirements(ctx)
    lf = config.lock_file

    if not lf.exists() or not can_lock(requirements):
        return requirements, False

    with lf.open(encoding="utf-8") as f:
        toml = tomlkit.load(f)

    if ctx not in toml:
        toml[ctx] = tomlkit.table()
    lf_toml_ctx = toml[ctx]
    requirements_hash = calculate_hash(requirements)
    if lf_toml_ctx.get("hash") == requirements_hash:
        locked_requirements = lf_toml_ctx.get("requirements")
        return {**requirements, "requirements": locked_requirements}, False

    locked_requirements = _freeze(ctx, requirements, quiet)
    lf_toml_ctx["requirements"] = locked_requirements
    lf_toml_ctx["hash"] = requirements_hash
    post_install = requirements.get("post-install")
    if post_install:
        lf_toml_ctx["post-install"] = post_install
    with lf.open("w", encoding="utf-8", newline="") as f:
        tomlkit.dump(toml, f)
    return lf_toml_ctx, True


def _freeze(ctx_name, requirements, quiet):
    cmd = [UV_EXE, "pip", "compile", "--universal", "--no-annotate", "--no-header"]
    if quiet:
        cmd.append("--quiet")
    else:
        print(f"{pw.BLUE}locking {pw.CYAN}{ctx_name}{pw.BLUE} requirements{pw.RESET}", file=sys.stderr)
    cmd.append("-")
    requirements_string = "\n".join(requirements["requirements"])
    proc_result = subprocess.run(cmd, input=requirements_string.encode("utf-8"), check=False, capture_output=True)
    sys.stderr.buffer.write(proc_result.stderr)
    if proc_result.returncode != 0:
        raise Warning(f"Failed to lock {ctx_name} requirements.")
    return sorted([line.strip() for line in proc_result.stdout.decode("utf-8").splitlines() if line])
