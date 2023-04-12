from pathlib import Path

import pytest

from pyprojectx.config import Config


def test_no_config():
    config = Config(Path(__file__).parent.with_name("data").joinpath("test-no-config.toml"))
    assert config.get_tool_requirements("tool") == {"requirements": [], "post-install": None}
    assert not config.is_tool("tool")
    assert config.get_alias("alias") == (None, None)


def test_no_tool_config():
    config = Config(Path(__file__).parent.with_name("data").joinpath("test-no-tool-config.toml"))
    assert config.get_alias("run") == (None, "run command")
    with pytest.raises(
        Warning, match=r"Invalid alias wrong-tool-alias: 'wrong-tool' is not defined in \[tool.pyprojectx\]"
    ):
        config.get_alias("wrong-tool-alias")


def test_tool_config():
    config = Config(Path(__file__).parent.with_name("data").joinpath("test.toml"))

    assert config.is_tool("tool-1")
    assert config.get_tool_requirements("tool-1") == {"requirements": ["req1", "req2"], "post-install": None}

    assert config.is_tool("tool-2")
    assert config.get_tool_requirements("tool-2") == {"requirements": ["tool2 requirement"], "post-install": None}

    assert config.is_tool("tool-3")
    assert config.get_tool_requirements("tool-3") == {"requirements": ["req1", "req2", "req3"], "post-install": None}

    assert config.is_tool("tool-4")
    assert config.get_tool_requirements("tool-4") == {"requirements": ["tool-4-req1"], "post-install": None}

    assert config.is_tool("tool-5")
    assert config.get_tool_requirements("tool-5") == {
        "requirements": ["tool-5-req1", "tool-5-req2"],
        "post-install": "tool-5 && pw@alias-1",
    }

    assert not config.is_tool("nope")
    assert config.get_tool_requirements("nope") == {"requirements": [], "post-install": None}


def test_alias_config():
    config = Config(Path(__file__).parent.with_name("data").joinpath("test.toml"))
    assert config.get_alias("alias-1") == ("tool-1", "tool-1 arg")
    assert config.get_alias("alias-2") == ("tool-2", "tool-2 arg1 arg2")
    assert config.get_alias("alias-3") == ("tool-1", "command arg")
    assert config.get_alias("alias-4") == ("tool-2", "command --default @arg:x")
    assert config.get_alias("combined-alias") == (None, "pw@alias-1 && pw@alias-2 pw@shell-command")
    assert config.get_alias("shell-command") == (None, "ls -al")
    assert config.get_alias("backward-compatible-tool-ref") == ("tool-1", "command arg")


def test_os_specific_alias_config(mocker):
    config = Config(Path(__file__).parent.with_name("data").joinpath("test.toml"))
    assert config.get_alias("os-specific") == (None, "cmd")

    mocker.patch("sys.platform", "my-os")
    config = Config(Path(__file__).parent.with_name("data").joinpath("test.toml"))
    assert config.get_alias("os-specific") == (None, "my-os-cmd")


def test_invalid_toml():
    with pytest.raises(Warning, match=r".+invalid.toml: Illegal character"):
        Config(Path(__file__).parent.with_name("data").joinpath("invalid.toml"))


def test_unexisting_toml():
    with pytest.raises(Warning, match=r"No such file or directory"):
        Config(Path(__file__).parent.with_name("data").joinpath("unexisting.toml"))


@pytest.mark.parametrize(
    ("shorcut", "aliases"),
    [
        ("aaa-bbb-ccc", ["aaa-bbb-ccc"]),
        ("aaaBbbDdd", ["aaaBbbDdd"]),
        ("b123-c123-d123", ["b123-c123-d123"]),
        ("c123D123", ["c123D123"]),
        ("d123-E123", ["d123-E123"]),
        ("aBC", ["aaa-bbb-ccc"]),
        ("aaBbCc", ["aaa-bbb-ccc"]),
        ("e", []),
        ("aC", []),
        ("A", []),
        ("E", ["E"]),
        ("a", ["aaa-bbb-ccc", "aaaBbbDdd"]),
        ("aB", ["aaa-bbb-ccc", "aaaBbbDdd"]),
        ("b", ["b123-c123-d123"]),
        ("bCD", ["b123-c123-d123"]),
        ("c1D1", ["c123D123"]),
        ("dE", ["d123-E123"]),
    ],
)
def test_find_aliases(shorcut, aliases):
    config = Config(Path(__file__).parent.with_name("data").joinpath("alias-abbreviations.toml"))
    assert config.find_aliases(shorcut) == aliases
