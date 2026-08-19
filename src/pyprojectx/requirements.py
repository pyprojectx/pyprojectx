import re
from pathlib import Path
from typing import Optional

import tomlkit
from tomlkit.toml_file import TOMLFile

from pyprojectx.config import MAIN, Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.wrapper import pw

requirement_regexp = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)")
ctx_requirement_regexp = re.compile(r"^([\w.-]+)\s*:\s*(.+)$")


def add_requirement(requirement: str, toml_path: Path, venvs_dir: Path, quiet: False, prerelease=None):
    if not toml_path.exists():
        toml_path.touch()
    toml_file = TOMLFile(toml_path)
    toml = toml_file.read()
    ctx, req_spec = _split_ctx_and_requirement(requirement)
    req_specs = re.split(r"\s*,\s*", req_spec)
    toml, requirements = _get_or_add_requirements(toml, ctx)
    for spec in req_specs:
        _check_already_met(requirements, spec, ctx)
    _check_is_installable(req_specs, ctx, Config(toml_path).get_requirements(ctx), venvs_dir, quiet, prerelease)
    for spec in req_specs:
        requirements.append(spec)
    toml_file.write(toml)


def _get_or_add_requirements(toml, ctx: str):
    if not toml.get("tool"):
        toml["tool"] = tomlkit.table()
    if not toml["tool"].get("pyprojectx"):
        toml["tool"]["pyprojectx"] = tomlkit.table()
    pyprojectx = toml["tool"]["pyprojectx"]

    requirements = None
    if not pyprojectx.get(ctx):
        pyprojectx.add(ctx, [])
        requirements = pyprojectx[ctx]
    else:
        requirements_config = pyprojectx[ctx]
        if isinstance(requirements_config, str):
            pyprojectx.pop(ctx)
            pyprojectx.add(ctx, requirements_config.splitlines())
            requirements = pyprojectx[ctx]
        elif isinstance(requirements_config, list):
            requirements = requirements_config
        elif isinstance(requirements_config, dict):
            reqs = requirements_config.get("requirements")
            if isinstance(reqs, str):
                requirements_config.pop("requirements")
                requirements_config.add("requirements", reqs.splitlines())
                requirements = requirements_config["requirements"]
            elif isinstance(reqs, list):
                requirements = reqs
        if not requirements:
            raise Warning(f"{pw.RED}{ctx} has invalid requirements. Check your pyproject.toml file{pw.RESET}")
    return toml, requirements


def _split_ctx_and_requirement(requirement: str) -> tuple:
    match = ctx_requirement_regexp.match(requirement)
    if not match:
        return MAIN, requirement
    prefix, rest = match.group(1), match.group(2)
    # URL schemes (file://, https://) are not contexts. VCS refs (git+https://) never match at all,
    # because '+' is not part of the prefix character class.
    if rest.startswith("//"):
        return MAIN, requirement
    return prefix, rest


def _normalize_requirement_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirement_name(req_spec: str) -> Optional[str]:
    """Extract the normalized package name of a requirement, or None if it doesn't start with one.

    URLs and VCS references (https://…, git+https://…, git+git@…) start with a scheme, not a package
    name, so they have nothing to compare against and are never reported as duplicates.
    """
    stripped = req_spec.strip()
    if not stripped or stripped.startswith("-"):
        return None
    match = requirement_regexp.match(stripped)
    if not match or stripped[match.end() : match.end() + 1] in {"+", ":"}:
        return None
    return _normalize_requirement_name(match.group(1))


def _check_already_met(requirements, req_spec, ctx):
    req_name = _requirement_name(req_spec)
    if not req_name:
        return
    for r in requirements:
        if _requirement_name(r) == req_name:
            raise Warning(f"{pw.RED}{req_name} is already a requirement in {ctx}")


def _check_is_installable(req_specs, ctx, requirements, venvs_dir, quiet, prerelease):  # noqa: PLR0913, PLR0917
    env = IsolatedVirtualEnv(venvs_dir, ctx, requirements, prerelease)
    if not env.is_installed:
        env.install(quiet=quiet)
    env.check_is_installable(req_specs, quiet)
