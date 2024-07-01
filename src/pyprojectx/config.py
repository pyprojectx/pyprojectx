import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import zip_longest
from pathlib import Path
from typing import Optional

import tomlkit

from pyprojectx.wrapper.pw import BLUE, CYAN, RESET

MAIN = "main"
PROJECT_DIR = "@PROJECT_DIR"
DEFAULT_SCRIPTS_DIR = "bin"
LOCK_FILE = "pw.lock"


@dataclass
class AliasCommand:
    """Encapsulates an alias command configured in the [tool.pyprojectx.alias] section."""

    cmd: str
    cwd: Optional[str] = None
    shell: Optional[str] = None
    env: dict[str, str] = field(default_factory=dict)
    ctx: Optional[str] = None


class Config:
    """Encapsulates the PyprojectX config inside a toml file."""

    def __init__(self, toml_path: Path) -> None:
        """:param toml_path: The toml config file"""
        self._toml_path = toml_path
        try:
            with toml_path.open("rb") as f:
                toml_dict = tomlkit.load(f)
        except Exception as e:
            raise Warning(f"Could not parse {toml_path}: {e}") from e

        project_path = toml_path.parent.absolute()
        self._contexts = toml_dict.get("tool", {}).get("pyprojectx", {}).copy()
        self._aliases = self._contexts.pop("aliases", {})
        self.env = self._contexts.pop("env", {})
        self.prerelease = self._contexts.pop("prerelease", None)
        if not isinstance(self.env, dict):
            msg = "Invalid config: 'env' must be a dictionary"
            raise Warning(msg)
        self.project_dir = str(project_path)
        self.cwd = self._contexts.pop("cwd", self.project_dir)
        if not isinstance(self.cwd, str):
            msg = "Invalid config: 'cwd' must be a string"
            raise Warning(msg)
        self.shell = self._contexts.pop("shell", None)
        if self.shell and not isinstance(self.shell, str):
            msg = "Invalid config: 'shell' must be a string"
            raise Warning(msg)
        scripts_dir = self._contexts.pop("scripts_dir", DEFAULT_SCRIPTS_DIR)
        if not isinstance(scripts_dir, str):
            msg = "Invalid config: 'scripts_dir' must be a string"
            raise Warning(msg)
        self._merge_os_config()
        self.scripts_path = project_path / scripts_dir
        self.lock_file = project_path / LOCK_FILE

    def show_info(self, cmd, error=False):
        alias_cmds = self.get_alias(cmd)
        out = sys.stderr if error else sys.stdout
        if alias_cmds:
            print(f"{cmd}{BLUE} is an alias in {CYAN}{self._toml_path.absolute()}", file=sys.stderr)
            for alias_cmd in alias_cmds:
                if alias_cmd.ctx:
                    print(f"{BLUE}and runs in the {CYAN}{alias_cmd.ctx}{BLUE} tool context", file=sys.stderr)
                print(f"{BLUE}command:{RESET}", file=sys.stderr)
                print(alias_cmd.cmd, file=out)
        elif self.get_script_path(cmd).exists():
            print(f"{cmd}{BLUE} is a script in {CYAN}{self.scripts_path.absolute()}", file=sys.stderr)
        elif self.is_ctx(cmd):
            print(f"{cmd}{BLUE} is a tool context in {CYAN}{self._toml_path.absolute()}", file=sys.stderr)
            print(f"{BLUE}requirements:{RESET}", file=sys.stderr)
            print(self.get_requirements(cmd), file=out)
        else:
            if cmd:
                print(
                    f"{cmd}{BLUE} is not configured as tool context or alias in {self._toml_path.absolute()}:{RESET}",
                    file=sys.stderr,
                )
                if self.is_ctx(MAIN):
                    print(f"{cmd}{BLUE} would run in the main context.{RESET}", file=sys.stderr)
                else:
                    print(f"{cmd}{BLUE} cannot run because there is no main context.{RESET}", file=sys.stderr)
            print(f"{BLUE}available aliases:{RESET}", file=sys.stderr)
            print("\n".join(self._aliases.keys()), file=out)
            print(f"{BLUE}available scripts:{RESET}", file=sys.stderr)
            print("\n".join(self._get_scripts()), file=out)
            print(f"{BLUE}available tool contexts:{RESET}", file=sys.stderr)
            print("\n".join(self._contexts.keys() - ["aliases", "os"]), file=out)

    def get_requirements(self, key) -> dict:
        """Get the requirements (dependencies) for a configured tool context in the [tool.pyprojectx] section.

        The requirements can either be specified as a string, a list of strings or an object with requirements and
        post-install as keys.
        A multiline string is treated as one requirement per line.
        :param key: The key (tool context name) to look for
        :return: a dict with the requirements as a list and the post-install script, or None if key is not found
        """
        requirements_config = self._contexts.get(key)
        post_install = None
        venv_dir = None
        requirements = []
        if isinstance(requirements_config, str):
            requirements = requirements_config.splitlines()
        if isinstance(requirements_config, list):
            requirements = requirements_config
        if isinstance(requirements_config, dict):
            reqs = requirements_config.get("requirements")
            if isinstance(reqs, str):
                requirements = reqs.splitlines()
            if isinstance(reqs, list):
                requirements = reqs
            post_install = requirements_config.get("post-install")
            venv_dir = requirements_config.get("dir")
            if venv_dir:
                venv_dir = venv_dir.replace(PROJECT_DIR, self.project_dir)
        return {"requirements": sorted(requirements), "post-install": post_install, "dir": venv_dir}

    def get_ctx_or_main(self, ctx=None):
        """Return the given context if it exists, otherwise return the main context if it exists.

        @param ctx: The context to look for
        """
        if ctx and self.is_ctx(ctx):
            return ctx
        if self.is_ctx(MAIN):
            return MAIN
        return None

    def get_context_names(self) -> Iterable[str]:
        """Return all context names in the [tool.pyprojectx] section."""
        return self._contexts.keys()

    def is_ctx(self, key) -> bool:
        """Check whether a key (context name) exists in the [tool.pyprojectx] section.

        :param key: The key (context name) to look for
        :return: True if the key exists in the [tool.pyprojectx] section.
        """
        return key and self._contexts.get(key) is not None

    def get_alias(self, key) -> list[AliasCommand]:
        """Get an alias command configured in the [tool.pyprojectx.alias] section.

        The alias is considered to be part of a tool context if:
         * its command starts with the name of the tool context
         * the command starts with '@tool-name:'
         * the alias explicitly specifies the tool context with the 'ctx' key
        :param key: The key (name) of the alias
        :return: A list of aliases or an empty list if there is no alias with the given key.
        """
        alias = self._aliases.get(key) if key else None
        if not alias:
            return []
        alias_config = {"ctx": None, "env": {}, "cwd": self.cwd, "shell": self.shell}
        if isinstance(alias, dict):
            alias_config.update(alias)
            if alias_config.get("ctx") and not isinstance(alias_config["ctx"], str):
                raise Warning(f"Invalid alias {key}: 'ctx' must be a string")
            if not isinstance(alias_config["env"], dict):
                raise Warning(f"Invalid alias {key}: 'env' must be a dictionary")
            if not isinstance(alias_config["cwd"], str):
                raise Warning(f"Invalid alias {key}: 'cwd' must be a string")
            alias_cmd = alias_config.get("cmd")
        else:
            alias_cmd = alias
        if isinstance(alias_cmd, str):
            alias_config["cmd"] = [alias_cmd]
        elif isinstance(alias_cmd, list):
            alias_config["cmd"] = alias_cmd

        return [self._build_alias_command(cmd, alias_config, key) for cmd in alias_config.get("cmd", [])]

    def _build_alias_command(self, cmd, alias_config, key) -> AliasCommand:
        ctx = self.get_ctx_or_main()
        alias_cmd = cmd
        if re.match(r"^@?[\w|-]+\s*:\s*", cmd):
            ctx, alias_cmd = re.split(r"\s*:\s*", cmd, maxsplit=1)
            if ctx.startswith("@"):
                ctx = ctx[1:]
        elif alias_config.get("ctx"):
            ctx = alias_config["ctx"]
        else:
            candidate = cmd.split()[0]
            if self.is_ctx(candidate):
                ctx = candidate
        if ctx and not self.is_ctx(ctx):
            raise Warning(f"Invalid alias {key}: '{ctx}' is not defined in [tool.pyprojectx]")

        return AliasCommand(
            alias_cmd,
            ctx=ctx,
            env=alias_config["env"],
            cwd=self.get_cwd(alias_config["cwd"]),
            shell=alias_config["shell"],
        )

    def is_alias(self, key) -> bool:
        """Check whether a key (alias name) exists in the [tool.pyprojectx.alias] section.

        :param key: The key (alias name) to look for
        :return: True if the key exists in the [tool.pyprojectx.alias] section.
        """
        return bool(self._aliases.get(key))

    def get_script_path(self, script):
        return (self.scripts_path / f"{script}.py").absolute()

    def find_aliases_or_scripts(self, abbrev: str) -> list[str]:
        """Find all alias keys and/or scripts in scripts_dir that match the abbreviation.

        The abbreviation can use camel case patterns that are expanded to match camel case and kebab case names.
        For example the pattern foBa (or even fB) matches fooBar and foo-bar.
        If the abbreviation is exactly equal to an alias key or script name, only that key is returned, even if the
        abbreviation matches other alias keys.
        :param abbrev: abbreviated or full alias key to search for
        :return: a list of matching alias keys and/or scripts
        """
        aliases_and_scripts = [*self._aliases.keys(), *self._get_scripts()]
        if abbrev in aliases_and_scripts:
            return [abbrev]

        return [name for name in aliases_and_scripts if camel_match(abbrev, name)]

    def get_cwd(self, cwd=None):
        _cwd = cwd or self.cwd
        return _cwd.replace(PROJECT_DIR, self.project_dir)

    def __repr__(self):
        return str(self._contexts)

    def _merge_os_config(self):
        os_dict = self._contexts.pop("os", {})
        for os_key in os_dict:
            if sys.platform.startswith(os_key) and isinstance(os_dict[os_key], dict):
                self.shell = os_dict[os_key].pop("shell", self.shell)
                self._aliases.update(os_dict[os_key].get("aliases", {}))

    def _get_scripts(self):
        return sorted([f.name.replace(".py", "") for f in self.scripts_path.glob("*.py") if f.is_file()])


def camel_match(abbrev, key):
    abbrev_parts = to_camel_parts(abbrev)
    full_parts = to_camel_parts(key)
    return all(f.startswith(s) for s, f in zip_longest(abbrev_parts, full_parts, fillvalue=""))


def to_camel_parts(key):
    if not key:
        return []
    if len(key) < 2:  # noqa: PLR2004
        return [key]
    camel = re.sub(r"(-\w)", lambda m: m.group(0)[1].upper(), key)
    return filter(len, re.split("([A-Z][^A-Z]*)", camel[0].lower() + camel[1:]))
