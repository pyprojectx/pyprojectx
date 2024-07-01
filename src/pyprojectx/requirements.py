import re
from pathlib import Path

import tomlkit
from tomlkit.toml_file import TOMLFile

from pyprojectx.config import MAIN, Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.wrapper import pw

requirement_regexp = re.compile(r"^([^=<>~!]+)")


def add_requirement(requirement: str, toml_path: Path, venvs_dir: Path, quiet: False, prerelease=None):
    if not toml_path.exists():
        toml_path.touch()
    toml_file = TOMLFile(toml_path)
    toml = toml_file.read()
    if ":" in requirement:
        ctx, req_spec = re.split(r"\s*:\s*", requirement, maxsplit=1)
    else:
        ctx = MAIN
        req_spec = requirement
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


def _check_already_met(requirements, req_spec, ctx):
    match = requirement_regexp.match(req_spec)
    if match:
        req_name = match[1]
        for r in requirements:
            if r.startswith(req_name):
                raise Warning(f"{pw.RED}{req_name} is already a requirement in {ctx}")


def _check_is_installable(req_specs, ctx, requirements, venvs_dir, quiet, prerelease):  # noqa: PLR0913
    env = IsolatedVirtualEnv(venvs_dir, ctx, requirements, prerelease)
    if not env.is_installed:
        env.install(quiet=quiet)
    env.check_is_installable(req_specs, quiet)
