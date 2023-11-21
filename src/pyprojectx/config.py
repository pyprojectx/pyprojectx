import re
import sys
from dataclasses import dataclass, field
from itertools import zip_longest
from pathlib import Path
from typing import Dict, List, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pyprojectx.wrapper.pw import BLUE, CYAN, RESET

MAIN = "main"
PROJECT_DIR = "@PROJECT_DIR"


@dataclass
class AliasCommand:
    """Encapsulates an alias command configured in the [tool.pyprojectx.alias] section."""

    cmd: str
    cwd: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    ctx: Optional[str] = None


class Config:
    """Encapsulates the PyprojectX config inside a toml file."""

    def __init__(self, toml_path: Path) -> None:
        """:param toml_path: The toml config file"""
        self._toml_path = toml_path
        try:
            with toml_path.open("rb") as f:
                toml_dict = tomllib.load(f)
                self._contexts = toml_dict.get("tool", {}).get("pyprojectx", {})
                self._aliases = self._merge_os_aliases()
                self.env = self._contexts.get("env", {})
                self.project_dir = str(toml_path.parent.absolute())
                self.cwd = self._contexts.get("cwd", self.project_dir)
        except Exception as e:  # noqa: BLE001
            raise Warning(f"Could not parse {toml_path}: {e}") from e
        if not isinstance(self.env, dict):
            msg = "Invalid config: 'env' must be a dictionary"
            raise Warning(msg)
        if not isinstance(self.cwd, str):
            msg = "Invalid config: 'cwd' must be a string"
            raise Warning(msg)

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
        elif self.is_ctx(cmd):
            print(f"{cmd}{BLUE} is a tool context in {CYAN}{self._toml_path.absolute()}", file=sys.stderr)
            print(f"{BLUE}requirements:{RESET}", file=sys.stderr)
            print(self.get_ctx_requirements(cmd), file=out)
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
            print(f"{BLUE}available tool contexts:{RESET}", file=sys.stderr)
            print("\n".join(self._contexts.keys() - ["aliases", "os"]), file=out)

    def get_ctx_requirements(self, key) -> dict:
        """Get the requirements (dependencies) for a configured tool context in the [tool.pyprojectx] section.

        The requirements can either be specified as a string, a list of strings or an object with requirements and
        post-install as keys.
        A multiline string is treated as one requirement per line.
        :param key: The key (tool context name) to look for
        :return: a dict with the requirements as a list and the post-install script, or None if key is not found
        """
        requirements_config = self._contexts.get(key)
        post_install = None
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
        return {"requirements": requirements, "post-install": post_install}

    def get_ctx_or_main(self, ctx=None):
        """Return the given context if it exists, otherwise return the main context if it exists.

        @param ctx: The context to look for
        """
        if ctx and self.is_ctx(ctx):
            return ctx
        if self.is_ctx(MAIN):
            return MAIN
        return None

    def is_ctx(self, key) -> bool:
        """Check whether a key (context name) exists in the [tool.pyprojectx] section.

        :param key: The key (context name) to look for
        :return: True if the key exists in the [tool.pyprojectx] section.
        """
        return self._contexts.get(key) is not None

    def get_alias(self, key) -> List[AliasCommand]:
        """Get an alias command configured in the [tool.pyprojectx.alias] section.

        The alias is considered to be part of a tool context if:
         * its command starts with the name of the tool context
         * the command starts with '@tool-name:'
         * the alias explicitly specifies the tool context with the 'ctx' key
        :param key: The key (name) of the alias
        :return: A list of aliases or an empty list if there is no alias with the given key.
        """
        alias = self._aliases.get(key)
        if not alias:
            return []
        alias_config = {"ctx": None, "env": {}, "cwd": self.cwd}
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

        return AliasCommand(alias_cmd, ctx=ctx, env=alias_config["env"], cwd=self.get_cwd(alias_config["cwd"]))

    def is_alias(self, key) -> bool:
        """Check whether a key (alias name) exists in the [tool.pyprojectx.alias] section.

        :param key: The key (alias name) to look for
        :return: True if the key exists in the [tool.pyprojectx.alias] section.
        """
        return bool(self._aliases.get(key))

    def find_aliases(self, abbrev: str) -> List[str]:
        """Find all alias keys that match the abbreviation.

        The abbreviation can use camel case patterns that are expanded to match camel case and kebab case names.
        For example the pattern foBa (or even fB) matches fooBar and foo-bar.
        If the abbreviation is exactly equal to an alias key, only that key is returned, even if the abbreviation
        matches other alias keys.
        :param abbrev: abbreviated or full alias key to search for
        :return: a list of matching alias keys
        """
        if abbrev in self._aliases:
            return [abbrev]

        return [key for key in self._aliases if camel_match(abbrev, key)]

    def get_cwd(self, cwd=None):
        _cwd = cwd or self.cwd
        return _cwd.replace(PROJECT_DIR, self.project_dir)

    def __repr__(self):
        return str(self._contexts)

    def _merge_os_aliases(self):
        aliases = self._contexts.get("aliases", {})
        os_dict = self._contexts.get("os", {})
        for os_key in os_dict:
            if sys.platform.startswith(os_key) and isinstance(os_dict[os_key], dict):
                aliases.update(os_dict[os_key].get("aliases", {}))
        return aliases


def camel_match(abbrev, key):
    abbrev_parts = to_camel_parts(abbrev)
    full_parts = to_camel_parts(key)
    return all(f.startswith(s) for s, f in zip_longest(abbrev_parts, full_parts, fillvalue=""))


def to_camel_parts(key):
    if not key:
        return []
    if len(key) < 2:  # noqa PLR2004
        return [key]
    camel = re.sub(r"(-\w)", lambda m: m.group(0)[1].upper(), key)
    return filter(len, re.split("([A-Z][^A-Z]*)", camel[0].lower() + camel[1:]))
