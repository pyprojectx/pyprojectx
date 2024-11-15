# ruff: noqa: PLR2004
import os.path
import sys
from pathlib import Path
from unittest.mock import ANY, call

import pytest
from pyprojectx.cli import _get_options, _run
from pyprojectx.env import PYTHON_EXE
from pyprojectx.wrapper import pw

PY_VER = f"py{sys.version_info.major}.{sys.version_info.minor}"
SCRIPTS_DIR = "Scripts" if sys.platform.startswith("win") else "bin"
UV_EXE = "uv.exe" if sys.platform.startswith("win") else "uv"


def test_parse_args():
    assert _get_options(["--toml", "an-option", "my-cmd"]).toml_path == Path("an-option")
    assert _get_options(["-t", "an-option", "my-cmd"]).toml_path == Path("an-option")
    assert _get_options(["my-cmd"]).toml_path == Path(pw.__file__).with_name("pyproject.toml")

    assert _get_options(["--install-dir", "an-option", "my-cmd"]).install_path == Path("an-option")

    assert _get_options(["--force-install", "my-cmd"]).force_install
    assert _get_options(["-f", "my-cmd"]).force_install
    assert not _get_options(["my-cmd"]).force_install

    assert _get_options(["-c", "my-cmd"]).clean
    assert not _get_options(["my-cmd"]).clean

    assert _get_options(["--verbose", "my-cmd"]).verbosity == 1
    assert _get_options(["--verbose", "--verbose", "my-cmd"]).verbosity == 2
    assert _get_options(["my-cmd"]).verbosity == 0
    assert _get_options(["--verbose", "--verbose", "-q", "my-cmd"]).verbosity == 0

    assert _get_options(["--install-px"]).install_px
    assert _get_options(["-i", "all"]).info

    assert _get_options(["my-cmd", "--in"]).cmd == "my-cmd"

    assert _get_options(["--upgrade"]).upgrade


def test_run_tool(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "tool-1"])

    venv_args = run_mock.mock_calls[0].args[0]
    assert venv_args[0].endswith(UV_EXE)
    assert venv_args[1] == "venv"
    assert venv_args[2].endswith(f"{tmp_dir.name}{os.sep}venvs{os.sep}tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}")
    assert venv_args[3:] == ["--prompt", "px-tool-1"]

    pip_install_args = run_mock.mock_calls[1].args[0]
    assert pip_install_args[0].endswith(UV_EXE)
    assert pip_install_args[1:5] == ["pip", "install", "-r", "-"]
    assert pip_install_args[5] == "--python"
    assert pip_install_args[6].endswith(
        f"{tmp_dir.name}{os.sep}venvs{os.sep}tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}"
        f"{os.sep}{SCRIPTS_DIR}{os.sep}{PYTHON_EXE}"
    )

    run_args = run_mock.mock_calls[2].args[0]
    run_kwargs = run_mock.mock_calls[2].kwargs
    assert len(run_args) == 1
    assert run_args[0] == "tool-1"
    path_env = run_kwargs["env"]["PATH"]
    assert (
        f"{tmp_dir.name}{os.sep}venvs{os.sep}tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}{os.sep}{SCRIPTS_DIR}"
        in path_env
    )
    assert run_kwargs["check"] is True


def test_run_tool_with_args(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "tool-1", "arg1", "@last arg"])

    run_mock.assert_called_with(ANY, shell=False, check=True, env=ANY, cwd=ANY, stdout=None)
    run_args = run_mock.mock_calls[2].args[0]
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

    run_mock.assert_called_with("tool-1 arg", shell=True, check=True, env=ANY, cwd=ANY, stdout=None)
    path_env = run_mock.mock_calls[2].kwargs["env"]["PATH"]
    assert (
        f"{tmp_dir.name}{os.sep}venvs{os.sep}"
        f"tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}{os.sep}{SCRIPTS_DIR}{os.path.pathsep}" in path_env
    )


def test_run_alias_with_ctx_with_args(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "alias-1", "alias-arg1", "alias-arg2"])

    run_mock.assert_called_with(
        'tool-1 arg "alias-arg1" "alias-arg2"', shell=True, check=True, env=ANY, cwd=ANY, stdout=None
    )


def test_run_explicit_alias_with_ctx_with_arg(tmp_dir, mocker):
    toml = Path(__file__).parent.with_name("data").joinpath("test.toml")
    run_mock = mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "alias-3", "alias-arg"])

    run_mock.assert_called_with('command arg "alias-arg"', shell=True, check=True, env=ANY, cwd=ANY, stdout=None)
    assert (
        f"{tmp_dir.name}{os.sep}venvs{os.sep}"
        f"tool-1-db298015454af73633c6be4b86b3f2e8-{PY_VER}{os.sep}{SCRIPTS_DIR}{os.path.pathsep}"
        in run_mock.mock_calls[2].kwargs["env"]["PATH"]
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
        stdout=None,
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

    run_mock.assert_called_with('ls -al "alias-arg"', shell=True, check=True, env=ANY, cwd=ANY, stdout=None)


def test_run_script(tmp_dir, mocker):
    data = Path(__file__).parent.with_name("data")
    toml = data / "test.toml"
    run_mock = mocker.patch("subprocess.run")

    _run(["path to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "script-a"])

    args = run_mock.call_args.args[0]
    assert len(args) == 2
    assert "python" in args[0]
    assert args[1] == (data / "scripts/script-a.py").absolute()
    kwargs = run_mock.call_args.kwargs
    assert "tool-1" in kwargs["env"]["PATH"], "the path of the scripts_ctx should be in the PATH"
    assert kwargs["env"]["ENV_VAR1"] == "ENV_VAR1"
    assert kwargs["check"]
    assert kwargs["cwd"] == "/cwd"
    assert not kwargs["shell"]


def test_run_aliased_script(tmp_dir, mocker):
    data = Path(__file__).parent.with_name("data")
    toml = data / "test.toml"
    run_mock = mocker.patch("subprocess.run")

    _run(["path to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "aS"])

    assert run_mock.call_args.args[0] == "python aliased-script.py --some-option"


def test_install_context(tmp_dir, mocker):
    data = Path(__file__).parent.with_name("data")
    toml = data / "test.toml"
    run_mock = mocker.patch("subprocess.run")

    _run(["path to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "--install-context", "main"])

    calls = [
        call(
            [ANY, "venv", ANY, "--prompt", "px-main"],
            stdout=ANY,
            check=True,
        ),
        call(
            [ANY, "pip", "install", "-r", "-", "--python", ANY],
            input=b"main-requirement",
            stdout=ANY,
            check=True,
        ),
        call("main-post-install", shell=True, check=True, env=ANY, cwd=ANY, stdout=ANY),
    ]
    run_mock.assert_has_calls(calls)


def test_install_non_existing_context(tmp_dir):
    data = Path(__file__).parent.with_name("data")
    toml = data / "test.toml"
    with pytest.raises(Warning, match=r"Invalid ctx: 'foo' is not defined in \[tool.pyprojectx\]"):
        _run(["path to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "--install-context", "foo"])


def test_info_without_arg_should_not_raise_exception(tmp_dir, capsys):
    data = Path(__file__).parent.with_name("data")
    toml = data / "test.toml"
    _run(["path to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "--info"])
    captured = capsys.readouterr()
    assert "alias-1" in captured.out
    assert "script-a" in captured.out
    assert "main" in captured.out


@pytest.mark.parametrize("cmd", ["", "my-cmd"])
def test_clean(tmp_dir, capsys, mocker, cmd):
    data = Path(__file__).parent.with_name("data")
    toml = data / "test.toml"
    run_mock = mocker.patch("subprocess.run")

    old_pyprojectx_dir = tmp_dir / "pyprojectx" / "old-pyprojectx"
    old_pyprojectx_dir.mkdir(parents=True)
    old_venv_dir = tmp_dir / "venvs" / "old-venv"
    old_venv_dir.mkdir(parents=True)

    _run(["path to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "--clean", cmd])

    captured = capsys.readouterr()
    assert captured.err == (
        f"{pw.CYAN}Removing {pw.BLUE}{old_pyprojectx_dir.resolve()}{pw.RESET}\n"
        f"{pw.CYAN}Removing {pw.BLUE}{old_venv_dir.resolve()}{pw.RESET}\n"
    )
    assert captured.out == ""
    if cmd:
        run_mock.assert_called_with([cmd], shell=False, check=True, env=ANY, cwd=ANY, stdout=ANY)
    else:
        run_mock.assert_not_called()
