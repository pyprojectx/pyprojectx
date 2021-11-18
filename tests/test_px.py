import re
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import pytest

spec = spec_from_loader("pw", SourceFileLoader("pw", str(Path(__file__).parent.parent.joinpath("pw"))))
pw = module_from_spec(spec)
spec.loader.exec_module(pw)


def test_parse_args_with_tool():
    toml = Path(__file__).with_name("test.toml")
    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "tool1"], toml)
    assert tool == "tool1"
    assert cmd == "tool1"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "tool1", "--pw-upgrade", "arg1", "arg2"], toml)
    assert tool == "tool1"
    assert cmd == "tool1 arg1 arg2"
    assert upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "tool-2"], toml)
    assert tool == "tool-2"
    assert cmd == "tool-2"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "tool3", "arg"], toml)
    assert tool == "tool3"
    assert cmd == "tool3 arg"
    assert not upgrade
    assert not clear


def test_parse_args_no_tool():
    toml = Path(__file__).with_name("test.toml")
    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "command"], toml)
    assert tool is None
    assert cmd == "command"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "command", "arg1", "arg2"], toml)
    assert tool is None
    assert cmd == "command arg1 arg2"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "--pw-upgrade", "command", "arg1"], toml)
    assert tool is None
    assert cmd == "command arg1"
    assert upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "--pw-clear", "command"], toml)
    assert tool is None
    assert cmd == "command"
    assert not upgrade
    assert clear

    with pytest.raises(Warning, match=re.escape(pw.HELP)):
        pw.parse_args(["path/to/pw"], toml)


def test_parse_args_with_alias():
    toml = Path(__file__).with_name("test.toml")
    aliases = pw.toml_aliases(toml)

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "run"], toml, aliases)
    assert tool == "tool1"
    assert cmd == "tool1 start"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "test", "my-test", "--pw-clear"], toml, aliases)
    assert tool == "tool-2"
    assert cmd == "tool-2 run test my-test"
    assert not upgrade
    assert clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "sub_tool", "--pw-upgrade", "arg1", "arg2"], toml, aliases)
    assert tool == "tool1"
    assert cmd == "sub_tool default_arg arg1 arg2"
    assert upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "sub-tool-2-alias", "arg1", "arg2"], toml, aliases)
    assert tool == "tool-2"
    assert cmd == "sub-tool-2 default:arg arg1 arg2"
    assert not upgrade
    assert not clear

    tool, cmd, upgrade, clear = pw.parse_args(["path/to/pw", "combined-alias", "arg1", "arg2"], toml, aliases)
    assert tool is None
    assert cmd == "path/to/pw run && path/to/pw test path/to/pw shell-command arg1 arg2"
    assert not upgrade
    assert not clear
