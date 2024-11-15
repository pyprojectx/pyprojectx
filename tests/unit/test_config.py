from pathlib import Path

import pytest
from pyprojectx.config import MAIN, AliasCommand, Config


def test_no_config():
    config = Config(Path(__file__).parent.with_name("data").joinpath("test-no-config.toml"))
    assert config.get_requirements("tool") == {"requirements": [], "post-install": None, "dir": None}
    assert not config.is_ctx("tool")
    assert config.get_alias("alias") == []


def test_no_ctx_config():
    data_dir = Path(__file__).parent.with_name("data")
    config = Config(data_dir / "test-no-tool-config.toml")
    assert config.get_alias("run") == [AliasCommand("run command", cwd=str(data_dir.absolute()))]
    with pytest.raises(
        Warning, match=r"Invalid alias wrong-tool-alias: 'wrong-tool' is not defined in \[tool.pyprojectx\]"
    ):
        config.get_alias("wrong-tool-alias")


def test_ctx_config():
    config = Config(Path(__file__).parent.with_name("data").joinpath("test.toml"))

    assert config.is_ctx("tool-1")
    assert config.get_requirements("tool-1") == {"requirements": ["req1", "req2"], "post-install": None, "dir": None}

    assert config.is_ctx("tool-2")
    assert config.get_requirements("tool-2") == {
        "requirements": ["tool2 requirement"],
        "post-install": None,
        "dir": None,
    }

    assert config.is_ctx("tool-3")
    assert config.get_requirements("tool-3") == {
        "requirements": ["req1", "req2", "req3"],
        "post-install": None,
        "dir": None,
    }

    assert config.is_ctx("tool-4")
    assert config.get_requirements("tool-4") == {"requirements": ["tool-4-req1"], "post-install": None, "dir": None}

    assert config.is_ctx("tool-5")
    assert config.get_requirements("tool-5") == {
        "requirements": ["tool-5-req1", "tool-5-req2"],
        "post-install": "tool-5 && pw@alias-1",
        "dir": None,
    }

    assert config.get_requirements("venv") == {
        "requirements": ["venv-requirement"],
        "post-install": None,
        "dir": "venv-dir",
    }

    assert not config.is_ctx("nope")
    assert config.get_requirements("nope") == {"requirements": [], "post-install": None, "dir": None}


def test_alias_config():
    data_dir = Path(__file__).parent.with_name("data")
    config = Config(data_dir / "test-shell.toml")
    assert config.get_alias("alias-1") == [AliasCommand("tool-1 arg", ctx="tool-1", cwd="/cwd", shell="default-shell")]
    assert config.get_alias("alias-2") == [
        AliasCommand("tool-2 arg1 arg2", ctx="tool-2", cwd="/cwd", shell="default-shell")
    ]
    assert config.get_alias("alias-3") == [AliasCommand("command arg", ctx="tool-1", cwd="/cwd", shell="default-shell")]
    assert config.get_alias("alias-4") == [
        AliasCommand("command --default @arg:x", ctx="tool-2", cwd="/cwd", shell="default-shell")
    ]
    assert config.get_alias("combined-alias") == [
        AliasCommand("pw@alias-1 && pw@alias-2 pw@shell-command", cwd="/cwd", ctx=MAIN, shell="default-shell")
    ]
    assert config.get_alias("alias-list") == [
        AliasCommand("pw@alias-1", cwd="/cwd", ctx=MAIN, shell="default-shell"),
        AliasCommand("pw@alias-2", cwd="/cwd", ctx=MAIN, shell="default-shell"),
        AliasCommand("pw@shell-command", cwd="/cwd", ctx=MAIN, shell="default-shell"),
    ]
    assert config.get_alias("alias-dict") == [
        AliasCommand(
            "alias-dict",
            ctx="tool-1",
            env={"ENV_VAR2": "ENV_VAR2"},
            cwd=str(data_dir.absolute()),
            shell="alias-shell",
        )
    ]
    assert config.get_alias("alias-dict-list") == [
        AliasCommand("alias-dict-list-1", ctx="tool-1", cwd="/cwd", shell="default-shell"),
        AliasCommand("alias-dict-list-2", ctx="tool-2", cwd="/cwd", shell="default-shell"),
    ]
    assert config.get_alias("shell-command") == [AliasCommand("ls -al", cwd="/cwd", ctx=MAIN, shell="default-shell")]
    assert config.get_alias("backward-compatible-tool-ref") == [
        AliasCommand("command arg", ctx="tool-1", cwd="/cwd", shell="default-shell")
    ]


def test_os_specific_alias_config(mocker):
    config = Config(Path(__file__).parent.with_name("data").joinpath("test-shell.toml"))
    assert config.get_alias("os-specific") == [AliasCommand("cmd", cwd="/cwd", ctx=MAIN, shell="default-shell")]

    mocker.patch("sys.platform", "my-os")
    config = Config(Path(__file__).parent.with_name("data").joinpath("test-shell.toml"))
    assert config.get_alias("os-specific") == [AliasCommand("my-os-cmd", cwd="/cwd", ctx=MAIN, shell="my-os-shell")]


def test_invalid_toml():
    with pytest.raises(Warning, match=r"Could not parse.+are not allowed in strings.+"):
        Config(Path(__file__).parent.with_name("data").joinpath("invalid.toml"))


@pytest.mark.parametrize(
    ("shortcut", "candidates"),
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
        ("a", ["aaa-bbb-ccc", "aaaBbbDdd", "aliased-script"]),
        ("aB", ["aaa-bbb-ccc", "aaaBbbDdd"]),
        ("b", ["b123-c123-d123"]),
        ("bCD", ["b123-c123-d123"]),
        ("c1D1", ["c123D123"]),
        ("dE", ["d123-E123"]),
        ("s", ["script-a", "script-b"]),
        ("script-a", ["script-a"]),
    ],
)
def test_find_aliases_or_scripts(shortcut, candidates):
    config = Config(Path(__file__).parent.with_name("data").joinpath("alias-abbreviations.toml"))
    assert config.find_aliases_or_scripts(shortcut) == candidates
