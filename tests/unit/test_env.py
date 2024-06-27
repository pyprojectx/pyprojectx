# ruff: noqa: PLR2004
import os
import subprocess
import sys
from unittest.mock import ANY

import pytest
from pyprojectx.env import IsolatedVirtualEnv, PYTHON_EXE
from pyprojectx.log import set_verbosity


def test_isolated_env_path(tmp_dir):
    env = IsolatedVirtualEnv(
        tmp_dir,
        "env-name",
        {
            "requirements": [
                "requirement1",
                "requirement2",
            ]
        },
    )
    assert (
        f"{tmp_dir.name}{os.sep}"
        f"env-name-57b6e92d262b77ef47fda82ab9b9c617-py{sys.version_info.major}.{sys.version_info.minor}"
        in str(env.path)
    )


def test_isolated_env_install(tmp_dir):
    env = IsolatedVirtualEnv(tmp_dir, "env-name", {})
    assert not env.is_installed

    env.install()
    assert env.scripts_path.exists()
    assert env.is_installed


def test_isolated_env_remove(tmp_dir):
    env = IsolatedVirtualEnv(tmp_dir, "env-name", {})
    env.install()
    assert env.path.exists()
    env.remove()
    assert not env.path.exists()


def test_isolation(tmp_dir):
    subprocess.check_call([sys.executable, "-c", "import pyprojectx.env"])
    env = IsolatedVirtualEnv(tmp_dir, "env-name", {})
    env.install()
    debug_import = "import sys; import os; print(os.linesep.join(sys.path));"
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call([str(env.scripts_path / PYTHON_EXE), "-c", f"{debug_import} import pyprojectx.env"])


def test_isolated_env_install_arguments(mocker, tmp_dir):
    run_mock = mocker.patch("subprocess.run")
    env = IsolatedVirtualEnv(tmp_dir, "env-name", {"requirements": ["some", "requirements"]})
    env.install()

    run_mock.assert_called()
    args = run_mock.call_args[0][0]
    assert args == [ANY, "pip", "install", "-r", ANY, "--python", ANY]


def test_run(tmp_dir, capfd):
    env = IsolatedVirtualEnv(
        tmp_dir,
        "env-name",
        {
            "requirements": [
                "virtualenv==20.10.0",
            ]
        },
    )
    env.install()
    captured = capfd.readouterr()
    assert "Creating virtualenv" in captured.err

    env.run("virtualenv --version", env={}, cwd=".")
    captured = capfd.readouterr()
    assert captured.out.startswith("virtualenv")

    env.run(["virtualenv", "--version"], env={}, cwd=".")
    captured = capfd.readouterr()
    assert captured.out.startswith("virtualenv")

    env.run("echo hello world", env={}, cwd=".")
    captured = capfd.readouterr()
    assert captured.out.strip() == "hello world"

    set_verbosity(1)
    path = "%PATH%" if sys.platform == "win32" else "$PATH"
    env.run(f"echo {path}", env={}, cwd=".")
    captured = capfd.readouterr()
    assert str(env.scripts_path.name) in captured.out
