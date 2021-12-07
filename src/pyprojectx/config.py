import re
import sys
from pathlib import Path
from typing import Iterable, Optional, Tuple

import tomli


class Config:
    """
    Encapsulates the PyprojectX config inside a toml file
    """

    def __init__(self, toml_path: Path) -> None:
        """
        :param toml_path: The toml config file
        """
        self._toml_path = toml_path
        try:
            with open(self._toml_path, "rb") as f:
                toml_dict = tomli.load(f)
                self._tools = toml_dict.get("tool", {}).get("pyprojectx", {})
                self._aliases = self._tools.get("aliases", {})
                self._os_aliases = self._merge_os_aliases()
        except Exception as e:
            raise Warning(f"Could not parse {self._toml_path}: {e}") from e

    def get_tool_requirements(self, key) -> Iterable[str]:
        """
        Get the requirements (dependencies) for a configured tool in the [tool.pyprojectx] section.
        The requirements can either be specified as a string or a list of strings.
        A multiline string is treated as one requirement per line.
        :param key: The key (tool name) to look for
        :return: the requirements as a list or None if key is not found
        """
        requirements = self._tools.get(key)
        if isinstance(requirements, list):
            return requirements
        if isinstance(requirements, str):
            return requirements.splitlines()
        return []

    def is_tool(self, key) -> bool:
        """
        Check whether a key (tool name) exists in the [tool.pyprojectx] section.
        :param key: The key (tool name) to look for
        :return: True if the key exists in the [tool.pyprojectx] section.
        """
        return self._tools.get(key) is not None

    def get_alias(self, key) -> Tuple[Optional[str], Optional[str]]:
        """
        Get an alias command configured in the [tool.pyprojectx.alias] section.
        The alias is considered to be part of a tool if its command starts with the name of the tool
        or if the the command starts with '@tool-name:'.
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

    def __repr__(self):
        return str(self._tools)

    def _merge_os_aliases(self):
        aliases = self._tools.get("aliases", {})
        os_dict = self._tools.get("os", {})
        for os_key in os_dict:
            if sys.platform.startswith(os_key) and isinstance(os_dict[os_key], dict):
                aliases.update(os_dict[os_key].get("aliases", {}))
        return aliases
