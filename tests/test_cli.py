# pylint: disable=protected-access
import os.path
import subprocess
from pathlib import Path
from unittest.mock import ANY

import pytest

from pyprojectx.cli import _get_options, _run


def test_parse_args():
    assert _get_options(["--toml", "an-option", "my-cmd"]).toml_path == Path("an-option")
    assert _get_options(["-t", "an-option", "my-cmd"]).toml_path == Path("an-option")
    assert _get_options(["my-cmd"]).toml_path == Path("pyproject.toml")

    assert _get_options(["--install-dir", "an-option", "my-cmd"]).install_path == Path("an-option")

    assert _get_options(["--force-install", "my-cmd"]).force_install
    assert _get_options(["-f", "my-cmd"]).force_install
    assert not _get_options(["my-cmd"]).force_install

    assert _get_options(["--verbose", "my-cmd"]).verbosity == 1
    assert _get_options(["-vv", "my-cmd"]).verbosity == 2
    assert _get_options(["my-cmd"]).verbosity == 0
    assert _get_options(["-vv", "-q", "my-cmd"]).verbosity == 0


def test_run_tool(tmp_dir, mocker):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "tool-1"])

    pip_install_args = subprocess.run.mock_calls[0].args[0]
    assert f"{tmp_dir}/venvs/tool-1-db298015454af73633c6be4b86b3f2e8-py3.9/bin/python" in str(pip_install_args[0])
    assert pip_install_args[1:-1] == ["-Im", "pip", "install", "--use-pep517", "--no-warn-script-location", "-r"]
    assert "build-reqs-" in pip_install_args[-1]

    run_args = subprocess.run.mock_calls[1].args[0]
    run_kwargs = subprocess.run.mock_calls[1].kwargs
    assert run_args == ["tool-1"]
    assert (
        f"{tmp_dir}/venvs/tool-1-db298015454af73633c6be4b86b3f2e8-py3.9/bin{os.path.pathsep}"
        in run_kwargs["env"]["PATH"]
    )
    assert run_kwargs["shell"] is False
    assert run_kwargs["check"] is True


def test_run_tool_with_args(tmp_dir, mocker):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "tool-1", "arg1", "@last arg"])

    subprocess.run.assert_called_with(["tool-1", "arg1", "@last arg"], shell=False, check=True, env=ANY)


def test_run_no_cmd(tmp_dir):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    with pytest.raises(SystemExit, match="2"):
        _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml)])


def test_run_unknown_tool(tmp_dir):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    with pytest.raises(
        SystemExit,
        match="1",
    ):
        _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "foo"])


def test_run_tool_alias(tmp_dir, mocker):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "alias-1"])

    subprocess.run.assert_called_with("tool-1 arg", shell=True, check=True, env=ANY)
    assert (
        f"{tmp_dir}/venvs/tool-1-db298015454af73633c6be4b86b3f2e8-py3.9/bin{os.path.pathsep}"
        in subprocess.run.call_args.kwargs["env"]["PATH"]
    )


def test_run_tool_alias_with_args(tmp_dir, mocker):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "alias-1", "alias-arg1", "alias-arg2"])

    subprocess.run.assert_called_with("tool-1 arg alias-arg1 alias-arg2", shell=True, check=True, env=ANY)


def test_run_explicit_tool_alias_with_arg(tmp_dir, mocker):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "alias-3", "alias-arg"])

    subprocess.run.assert_called_with("command arg alias-arg", shell=True, check=True, env=ANY)
    assert (
        f"{tmp_dir}/venvs/tool-1-db298015454af73633c6be4b86b3f2e8-py3.9/bin{os.path.pathsep}"
        in subprocess.run.call_args.kwargs["env"]["PATH"]
    )


def test_combined_alias_with_arg(tmp_dir, mocker):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    mocker.patch("subprocess.run")

    _run(["path/to/pyprojectx", "--install-dir", str(tmp_dir), "-t", str(toml), "combined-alias", "alias-arg"])

    subprocess.run.assert_called_with(
        f"path/to/pyprojectx --install-dir {tmp_dir} -t {toml} alias-1 && path/to/pyprojectx --install-dir {tmp_dir} "
        f"-t {toml} alias-2 path/to/pyprojectx --install-dir {tmp_dir} -t {toml} shell-command alias-arg",
        shell=True,
        check=True,
    )


def test_shell_command_alias(tmp_dir, mocker):
    toml = Path(__file__).with_name("data").joinpath("test.toml")
    mocker.patch("subprocess.run")

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

    subprocess.run.assert_called_with(
        "ls -al alias-arg",
        shell=True,
        check=True,
    )
