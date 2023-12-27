import re
import sys
from pathlib import Path

import tomlkit
from tomlkit.toml_file import TOMLFile

from pyprojectx.config import MAIN, Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.wrapper import pw

requirment_regexp = re.compile(r"^([^=<>~!]+)")


def add_requirement(requirement: str, toml_path: Path, venvs_dir: Path, quiet: bool):
    if not toml_path.exists():
        toml_path.touch()
    toml_file = TOMLFile(toml_path)
    toml = toml_file.read()
    if ":" in requirement:
        ctx, req_spec = requirement.split(":", 1)
    else:
        ctx = MAIN
        req_spec = requirement
    toml, requirements = _get_or_add_requirements(toml, ctx)
    _check_already_met(requirements, req_spec, ctx)
    _check_is_installable(req_spec, ctx, Config(toml_path).get_requirements(ctx), venvs_dir, quiet)
    requirements.append(req_spec)
    toml_file.write(toml)


def _get_or_add_requirements(toml, ctx: str):
    if not toml.get("tool"):
        toml["tool"] = tomlkit.table()
    if not toml["tool"].get("pyprojectx"):
        toml["tool"]["pyprojectx"] = tomlkit.table()
    pyprojectx = toml["tool"]["pyprojectx"]
    if not pyprojectx.get(ctx):
        pyprojectx.add(ctx, [])
        requirements = pyprojectx[ctx]
    else:
        requirements_config = pyprojectx[ctx]
        if isinstance(requirements_config, str):
            pyprojectx.pop(ctx)
            pyprojectx.add(ctx, requirements_config.splitlines())
            requirements = pyprojectx[ctx]
        if isinstance(requirements_config, list):
            requirements = requirements_config
        if isinstance(requirements_config, dict):
            reqs = requirements_config.get("requirements")
            if isinstance(reqs, str):
                requirements_config.pop("requirements")
                requirements_config.add("requirements", reqs.splitlines())
                requirements = requirements_config["requirements"]
            if isinstance(reqs, list):
                requirements = reqs
    return toml, requirements


def _check_already_met(requirements, req_spec, ctx):
    match = requirment_regexp.match(req_spec)
    if match:
        req_name = match[1]
        for r in requirements:
            if r.startswith(req_name):
                print(f"{pw.RED}{req_name} is already a requirement in {ctx}", file=sys.stderr)
                raise SystemExit(1)


def _check_is_installable(req_spec, ctx, requirements, venvs_dir, quiet):
    env = IsolatedVirtualEnv(venvs_dir, ctx, requirements)
    cmd = ["pip", "install", req_spec, "--dry-run"]
    if quiet:
        cmd.append("--quiet")
    if not env.is_installed:
        env.install(quiet)
    env.run(cmd, env={}, cwd=env.path)
