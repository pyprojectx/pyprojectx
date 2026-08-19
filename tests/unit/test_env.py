import os
import subprocess
import sys
from unittest.mock import ANY

import pytest
from pyprojectx.env import IsolatedVirtualEnv, PYTHON_EXE
from pyprojectx.hash import calculate_hash
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
        f"env-name-{calculate_hash({'requirements': ['requirement1', 'requirement2']})}"
        f"-py{sys.version_info.major}.{sys.version_info.minor}" in str(env.path)
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
    os.environ["INDEX_USR"] = "_user_"
    os.environ["INDEX_URL"] = "_url_"
    os.environ["REQ_VERSION"] = "_version_"
    env = IsolatedVirtualEnv(
        tmp_dir,
        "env-name",
        {
            "requirements": [
                "--index-url=https://${INDEX_USR}:${INDEX_URL}/simple",
                "$my-$req=$REQ_VERSION",
                "another-req=${REQ_VERSION}",
                "some",
                "requirements",
            ]
        },
    )
    env.install()

    run_mock.assert_called()
    args = run_mock.call_args[0][0]
    assert args == [ANY, "pip", "install", "-r", ANY, "--python", ANY]
    install_input = run_mock.call_args[1]["input"]
    assert (
        install_input
        == b"--index-url=https://_user_:_url_/simple\n$my-$req=$REQ_VERSION\nanother-req=_version_\nsome\nrequirements"
    )


def test_run(tmp_dir, capfd):
    env = IsolatedVirtualEnv(
        tmp_dir,
        "env-name",
        {
            "requirements": [
                "uv==0.4.30",
            ]
        },
    )
    env.install()
    captured = capfd.readouterr()
    assert "Creating virtual environment" in captured.err

    env.run("uv --version", env={}, cwd=".")
    captured = capfd.readouterr()
    assert captured.out.startswith("uv 0.4.30")

    env.run(["uv", "--version"], env={}, cwd=".")
    captured = capfd.readouterr()
    assert captured.out.startswith("uv 0.4.30")

    env.run("echo hello world", env={}, cwd=".")
    captured = capfd.readouterr()
    assert captured.out.strip() == "hello world"

    set_verbosity(1)
    path = "%PATH%" if sys.platform == "win32" else "$PATH"
    env.run(f"echo {path}", env={}, cwd=".")
    captured = capfd.readouterr()
    assert str(env.scripts_path.name) in captured.out


def _scripts_dir(venv_path):
    return venv_path / ("Scripts" if sys.platform == "win32" else "bin")


def test_custom_dir_requires_matching_install_marker(tmp_dir):
    custom = tmp_dir / "project-venv"
    _scripts_dir(custom).mkdir(parents=True)
    env = IsolatedVirtualEnv(tmp_dir, "venv", {"requirements": ["pycowsay"], "dir": str(custom)})
    assert env.uses_custom_dir
    assert not env.is_installed

    env.mark_installed()
    assert env.is_installed

    changed = IsolatedVirtualEnv(tmp_dir, "venv", {"requirements": ["other"], "dir": str(custom)})
    assert not changed.is_installed

    env.unmark_installed()
    assert not env.is_installed


def test_custom_dir_install_does_not_clear_existing_venv(tmp_dir, mocker):
    custom = tmp_dir / "project-venv"
    _scripts_dir(custom).mkdir(parents=True)
    run_mock = mocker.patch("subprocess.run")
    env = IsolatedVirtualEnv(tmp_dir, "venv", {"requirements": ["pycowsay"], "dir": str(custom)})
    env.install()

    venv_creates = [call for call in run_mock.call_args_list if call.args and call.args[0][1:2] == ["venv"]]
    assert venv_creates == []


def test_install_marker_stays_outside_the_venv(tmp_dir):
    custom = tmp_dir / "project-venv"
    _scripts_dir(custom).mkdir(parents=True)
    env = IsolatedVirtualEnv(tmp_dir, "venv", {"requirements": ["pycowsay"], "dir": str(custom)})
    env.mark_installed()

    assert env.install_marker_path.is_file()
    assert list(custom.iterdir()) == [_scripts_dir(custom)]


def test_locked_requirements_change_triggers_reinstall(tmp_dir):
    """The venv path is keyed on the configured requirements, the marker on the installed ones."""
    config = {"requirements": ["pycowsay"], "hash": "the-configured-hash"}
    env = IsolatedVirtualEnv(tmp_dir, "main", {**config, "requirements": ["pycowsay==0.0.0.1"]})
    _scripts_dir(env.path).mkdir(parents=True)
    env.mark_installed()
    assert env.is_installed

    relocked = IsolatedVirtualEnv(tmp_dir, "main", {**config, "requirements": ["pycowsay==0.0.0.2"]})
    assert relocked.path == env.path
    assert not relocked.is_installed


def test_post_install_change_triggers_reinstall(tmp_dir):
    env = IsolatedVirtualEnv(tmp_dir, "main", {"requirements": ["pycowsay"], "post-install": "echo one"})
    _scripts_dir(env.path).mkdir(parents=True)
    env.mark_installed()
    assert env.is_installed

    changed = IsolatedVirtualEnv(tmp_dir, "main", {"requirements": ["pycowsay"], "post-install": "echo two"})
    assert not changed.is_installed


def test_venv_without_marker_is_considered_installed(tmp_dir):
    """Venvs created before install markers existed must not all be reinstalled after an upgrade."""
    env = IsolatedVirtualEnv(tmp_dir, "main", {"requirements": ["pycowsay"]})
    _scripts_dir(env.path).mkdir(parents=True)
    assert env.is_installed


def test_failed_install_leaves_venv_uninstalled(tmp_dir, mocker):
    env = IsolatedVirtualEnv(tmp_dir, "main", {"requirements": ["pycowsay"]})
    _scripts_dir(env.path).mkdir(parents=True)
    env.mark_installed()
    mocker.patch("subprocess.run")
    mocker.patch.object(IsolatedVirtualEnv, "_install_requirements", side_effect=OSError("boom"))

    with pytest.raises(OSError, match="boom"):
        env.install()

    assert not env.is_installed


def test_remove_clears_the_install_marker(tmp_dir):
    env = IsolatedVirtualEnv(tmp_dir, "main", {"requirements": ["pycowsay"]})
    _scripts_dir(env.path).mkdir(parents=True)
    env.mark_installed()

    env.remove()

    assert not env.install_marker_path.exists()


def test_post_install_running_in_the_same_ctx_does_not_recurse(tmp_dir, mocker):
    """A post-install command may re-enter installation of its own context; it must find it installed."""
    env = IsolatedVirtualEnv(tmp_dir, "main", {"requirements": ["pycowsay"], "post-install": "@self-referencing"})
    mocker.patch("subprocess.run")
    mocker.patch.object(IsolatedVirtualEnv, "_install_requirements")
    _scripts_dir(env.path).mkdir(parents=True)
    seen = []

    env.install(post_install=lambda: seen.append(env.is_installed))

    assert seen == [True]
    assert env.is_installed


def test_failed_post_install_leaves_venv_uninstalled(tmp_dir, mocker):
    env = IsolatedVirtualEnv(tmp_dir, "main", {"requirements": ["pycowsay"], "post-install": "boom"})
    mocker.patch("subprocess.run")
    mocker.patch.object(IsolatedVirtualEnv, "_install_requirements")
    _scripts_dir(env.path).mkdir(parents=True)

    def failing_post_install():
        raise subprocess.CalledProcessError(1, "boom")

    with pytest.raises(subprocess.CalledProcessError):
        env.install(post_install=failing_post_install)

    assert not env.is_installed
