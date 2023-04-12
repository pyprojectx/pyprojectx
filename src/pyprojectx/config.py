import re
import sys
from itertools import zip_longest
from pathlib import Path
from typing import List, Optional, Tuple

import tomli

from pyprojectx.wrapper.pw import BLUE, CYAN, RESET


class Config:
    """Encapsulates the PyprojectX config inside a toml file."""

    def __init__(self, toml_path: Path) -> None:
        """:param toml_path: The toml config file"""
        self._toml_path = toml_path
        try:
            with toml_path.open("rb") as f:
                toml_dict = tomli.load(f)
                self._tools = toml_dict.get("tool", {}).get("pyprojectx", {})
                self._aliases = self._tools.get("aliases", {})
                self._os_aliases = self._merge_os_aliases()
        except Exception as e:  # noqa: BLE001
            raise Warning(f"Could not parse {toml_path}: {e}") from e

    def show_info(self, cmd, error=False):
        tool, alias = self.get_alias(cmd)
        out = sys.stderr if error else sys.stdout
        if alias:
            print(f"{cmd}{BLUE} is an alias in {CYAN}{self._toml_path.absolute()}", file=sys.stderr)
            if tool:
                print(f"{BLUE}and runs in the {CYAN}{tool}{BLUE} tool context", file=sys.stderr)
            print(f"{BLUE}command:{RESET}", file=sys.stderr)
            print(alias, file=out)
        elif self.is_tool(cmd):
            print(f"{cmd}{BLUE} is a tool in {CYAN}{self._toml_path.absolute()}", file=sys.stderr)
            print(f"{BLUE}requirements:{RESET}", file=sys.stderr)
            print(self.get_tool_requirements(cmd), file=out)
        else:
            if cmd:
                print(
                    f"{cmd}{BLUE} is not configured as tool or alias in {self._toml_path.absolute()}:{RESET}",
                    file=sys.stderr,
                )
            print(f"{BLUE}available aliases:{RESET}", file=sys.stderr)
            print("\n".join(self._aliases.keys()), file=out)
            print(f"{BLUE}available tools:{RESET}", file=sys.stderr)
            print("\n".join(self._tools.keys() - ["aliases", "os"]), file=out)

    def get_tool_requirements(self, key) -> dict:
        """Get the requirements (dependencies) for a configured tool in the [tool.pyprojectx] section.

        The requirements can either be specified as a string, a list of strings or an object with requirements and
        post-install as keys.
        A multiline string is treated as one requirement per line.
        :param key: The key (tool name) to look for
        :return: a dict with the requirements as a list and the post-install script, or None if key is not found
        """
        requirements_config = self._tools.get(key)
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

    def is_tool(self, key) -> bool:
        """Check whether a key (tool name) exists in the [tool.pyprojectx] section.

        :param key: The key (tool name) to look for
        :return: True if the key exists in the [tool.pyprojectx] section.
        """
        return self._tools.get(key) is not None

    def get_alias(self, key) -> Tuple[Optional[str], Optional[str]]:
        """Get an alias command configured in the [tool.pyprojectx.alias] section.

        The alias is considered to be part of a tool if its command starts with the name of the tool
        or if the command starts with '@tool-name:'.
        :param key: The key (name) of the alias
        :return: A tuple containing the corresponding tool (or None) and
         the alias command (without the optional @tool-name part), or None if there is no alias with the given key.
        """
        alias_cmd = self._aliases.get(key)
        if not alias_cmd:
            return None, None
        if re.match(r"^@?[\w|-]+\s*:\s*", alias_cmd):
            tool, alias_cmd = re.split(r"\s*:\s*", alias_cmd, maxsplit=1)
            if tool.startswith("@"):
                tool = tool[1:]
            if not self.is_tool(tool):
                raise Warning(f"Invalid alias {key}: '{tool}' is not defined in [tool.pyprojectx]")
            return tool, alias_cmd
        tool = alias_cmd.split()[0]
        if self.is_tool(tool):
            return tool, alias_cmd
        return None, alias_cmd

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

    def __repr__(self):
        return str(self._tools)

    def _merge_os_aliases(self):
        aliases = self._tools.get("aliases", {})
        os_dict = self._tools.get("os", {})
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
