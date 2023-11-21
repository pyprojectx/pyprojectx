# ruff: noqa: PLR2004
import os.path
import sys
from pathlib import Path
from unittest.mock import ANY

import pytest

from pyprojectx.cli import _get_options, _run
from pyprojectx.wrapper import pw

PY_VER = f"py{sys.version_info.major}.{sys.version_info.minor}"
SCRIPTS_DIR = "Scripts" if sys.platform.startswith("win") else "bin"


def test_parse_args():
    assert _get_options(["--toml", "an-option", "my-cmd"]).toml_path == Path("an-option")
    assert _get_options(["-t", "an-option", "my-cmd"]).toml_path == Path("an-option")
    assert _get_options(["my-cmd"]).toml_path == Path(pw.__file__).with_name("pyproject.toml")

    assert _get_options(["--install-dir", "an-option", "my-cmd"]).install_path == Path("an-option")

    assert _get_options(["--force-install", "my-cmd"]).force_install
    assert _get_options(["-f", "my-cmd"]).force_install
    assert not _get_options(["my-cmd"]).force_install

    assert _get_options(["--verbose", "my-cmd"]).verbosity == 1
    assert _get_options(["--verbose", "--verbose", "my-cmd"]).verbosity == 2
    assert _get_options(["my-cmd"]).verbosity == 0
    assert _get_options(["--verbose", "--verbose", "-q", "my-cmd"]).verbosity == 0

    assert _get_options(["--init", "global"]).init
    assert _get_options(["-i", "all"]).info

    assert _get_options(["my-cmd", "--in"]).cmd == "my-cmd"
    assert not _get_options(["my-cmd", "--init"]).init

    assert _get_options(["--upgrade"]).upgrade


def test_run_tool(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "tool-1"])

    pip_install_args = _get_call_args(run_mock.mock_calls[0])
    first_arg = str(pip_install_args[0])
    assert (
        f"{tmp_dir.name}{os.sep}venvs{os.sep}"
        f"tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}{os.sep}{SCRIPTS_DIR}{os.sep}python" in first_arg
    )
    assert pip_install_args[1:-1] == ["-Im", "pip", "install", "--use-pep517", "--no-warn-script-location", "-r"]
    assert "build-reqs-" in str(pip_install_args[-1])

    run_args = _get_call_args(run_mock.mock_calls[1])
    run_kwargs = _get_call_kwargs(run_mock.mock_calls[1])
    assert len(run_args) == 1
    assert run_args[0] == "tool-1"
    path_env = run_kwargs["env"]["PATH"]
    assert (
        f"{tmp_dir.name}{os.sep}venvs{os.sep}tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}{os.sep}{SCRIPTS_DIR}"
        in path_env
    )
    assert run_kwargs["shell"] is False
    assert run_kwargs["check"] is True


def test_run_tool_with_args(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "tool-1", "arg1", "@last arg"])

    run_mock.assert_called_with(ANY, shell=False, check=True, env=ANY, cwd=ANY)
    run_args = _get_call_args(run_mock.mock_calls[1])
    assert run_args[0] == "tool-1"
    assert run_args[1:] == ["arg1", "@last arg"]


def test_run_no_cmd(tmp_dir):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    with pytest.raises(SystemExit, match="1"):
        _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml)])


def test_run_alias_with_ctx(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "alias-1"])

    run_mock.assert_called_with("tool-1 arg", shell=True, check=True, env=ANY, cwd=ANY)
    path_env = _get_call_kwargs(run_mock.mock_calls[1])["env"]["PATH"]
    assert (
        f"{tmp_dir.name}{os.sep}venvs{os.sep}"
        f"tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}{os.sep}{SCRIPTS_DIR}{os.path.pathsep}" in path_env
    )


def test_run_alias_with_ctx_with_args(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "alias-1", "alias-arg1", "alias-arg2"])

    run_mock.assert_called_with('tool-1 arg "alias-arg1" "alias-arg2"', shell=True, check=True, env=ANY, cwd=ANY)


def test_run_explicit_alias_with_ctx_with_arg(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "alias-3", "alias-arg"])

    run_mock.assert_called_with('command arg "alias-arg"', shell=True, check=True, env=ANY, cwd=ANY)
    assert (
        f"{tmp_dir.name}{os.sep}venvs{os.sep}"
        f"tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}{os.sep}{SCRIPTS_DIR}{os.path.pathsep}"
        in _get_call_kwargs(run_mock.mock_calls[1])["env"]["PATH"]
    )


def test_combined_alias_with_arg(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "combined-alias", "alias-arg"])

    run_mock.assert_called_with(
        f'"{Path("path to/pyprojectx").absolute()}" --install-dir "{tmp_dir.absolute()}" -t {toml.absolute()} '
        f'alias-1 && "{Path("path to/pyprojectx").absolute()}"'
        f' --install-dir "{tmp_dir.absolute()}" -t {toml.absolute()} alias-2 "{Path("path to/pyprojectx").absolute()}"'
        f' --install-dir "{tmp_dir.absolute()}" -t {toml.absolute()} shell-command "alias-arg"',
        shell=True,
        check=True,
        env=ANY,
        cwd=ANY,
    )


@pytest.mark.parametrize("cmd", ["tool-1", "alias-1", "alias-dict"])
def test_run_with_env(tmp_dir, mocker, cmd):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), cmd])

    args = run_mock.call_args
    assert args.kwargs["env"]["ENV_VAR1"] == "ENV_VAR1"
    if cmd == "alias-dict":
        assert args.kwargs["env"].get("ENV_VAR2") == "ENV_VAR2"
    else:
        assert args.kwargs["env"].get("ENV_VAR2") is None


def test_shell_command_alias(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(
        [
            "path/to/pyprojectx",
            "--install-dir",
            str(tmp_dir),
            "-t",
            str(toml),
            "shell-command",
            "alias-arg",
        ]
    )

    run_mock.assert_called_with(
        'ls -al "alias-arg"',
        shell=True,
        check=True,
        env=ANY,
        cwd=ANY,
    )


def _get_call_args(mock_call):
    if sys.version_info.major == 3 and sys.version_info.minor == 7:
        return mock_call[1][0]
    return mock_call.args[0]


def _get_call_kwargs(mock_call):
    if sys.version_info.major == 3 and sys.version_info.minor == 7:
        return mock_call[2]
    return mock_call.kwargs
