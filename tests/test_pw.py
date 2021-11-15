import re
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import pytest

spec = spec_from_loader("px", SourceFileLoader("px", str(Path(__file__).parent.parent.joinpath("px"))))
px = module_from_spec(spec)
spec.loader.exec_module(px)


def test_toml_pyprojectx_value():
    toml = Path(__file__).with_name("test.toml")
    assert px.toml_pyprojectx_value(toml, "tool1") == "tool1 pip"
    assert px.toml_pyprojectx_value(toml, "tool-2") == "tool2 pip"
    assert px.toml_pyprojectx_value(toml, "tool3") == "a b c"
    assert px.toml_pyprojectx_value(toml, "tool4") == "d e"
    assert px.toml_pyprojectx_value(toml, "tool5") == "tool5 pip"
    assert px.toml_pyprojectx_value(toml, "tool6") == "tool6 pip"
    assert px.toml_pyprojectx_value(toml, "xxx") is None


def test_toml_aliases():
    toml = Path(__file__).with_name("test.toml")
    assert px.toml_aliases(toml) == {
        "run": "tool1 start",
        "test": "tool-2 run test",
        "sub_tool": "tool1 : sub_tool default_arg",
        "sub-tool-2-alias": "tool-2 : sub-tool-2 default:arg",
        "combined-alias": "./px run && ./px test ./px shell-command",
        "shell-command": "ls -al",
    }


def test_parse_args_with_tool():
    toml = Path(__file__).with_name("test.toml")
    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "tool1"], toml)
    assert tool == "tool1"
    assert cmd == "tool1"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "tool1", "--px-upgrade", "arg1", "arg2"], toml)
    assert tool == "tool1"
    assert cmd == "tool1 arg1 arg2"
    assert upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "tool-2"], toml)
    assert tool == "tool-2"
    assert cmd == "tool-2"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "tool3", "arg"], toml)
    assert tool == "tool3"
    assert cmd == "tool3 arg"
    assert not upgrade
    assert not clear


def test_parse_args_no_tool():
    toml = Path(__file__).with_name("test.toml")
    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "command"], toml)
    assert tool is None
    assert cmd == "command"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "command", "arg1", "arg2"], toml)
    assert tool is None
    assert cmd == "command arg1 arg2"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "--px-upgrade", "command", "arg1"], toml)
    assert tool is None
    assert cmd == "command arg1"
    assert upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "--px-clear", "command"], toml)
    assert tool is None
    assert cmd == "command"
    assert not upgrade
    assert clear

    with pytest.raises(Warning, match=re.escape(px.HELP)):
        px.parse_args(["path/to/px"], toml)


def test_parse_args_with_alias():
    toml = Path(__file__).with_name("test.toml")
    aliases = px.toml_aliases(toml)

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "run"], toml, aliases)
    assert tool == "tool1"
    assert cmd == "tool1 start"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "test", "my-test", "--px-clear"], toml, aliases)
    assert tool == "tool-2"
    assert cmd == "tool-2 run test my-test"
    assert not upgrade
    assert clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "sub_tool", "--px-upgrade", "arg1", "arg2"], toml, aliases)
    assert tool == "tool1"
    assert cmd == "sub_tool default_arg arg1 arg2"
    assert upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "sub-tool-2-alias", "arg1", "arg2"], toml, aliases)
    assert tool == "tool-2"
    assert cmd == "sub-tool-2 default:arg arg1 arg2"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = px.parse_args(["path/to/px", "combined-alias", "arg1", "arg2"], toml, aliases)
    assert tool is None
    assert cmd == "path/to/px run && path/to/px test path/to/px shell-command arg1 arg2"
    assert not upgrade
    assert not clear
