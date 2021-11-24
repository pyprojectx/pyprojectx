import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from pyprojectx import pw


@pytest.fixture
def tmp_project(tmp_dir):
    toml = Path(__file__).with_name("data").joinpath("pw-test.toml")
    shutil.copyfile(toml, tmp_dir.joinpath(pw.PYPROJECT_TOML))
    pw_copy = Path(tmp_dir, "pw")
    pyprojectx_package = toml.parent.joinpath("../..")
    shutil.copyfile(pyprojectx_package.joinpath("src/pyprojectx/pw.py"), pw_copy)
    os.chmod(pw_copy, stat.S_IRWXU | stat.S_IRWXG)
    env = os.environ.copy()
    env["PYPROJECTX_PACKAGE"] = str(pyprojectx_package.absolute())
    return tmp_dir, env


def test_logs_and_stdout_with_quiet(tmp_project):
    project_dir, env = tmp_project
    pw_cmd = "pw" if sys.platform == "win32" else "./pw"
    cmd = f"{pw_cmd} -q pycowsay 'Hello px!'"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env)

    assert not proc_result.returncode
    assert (
        proc_result.stdout.decode("utf-8")
        == """
  ---------
< Hello px! >
  ---------
   \\   ^__^
    \\  (oo)\\_______
       (__)\\       )\\/\\
           ||----w |
           ||     ||

"""
    )
    assert proc_result.stderr.decode("utf-8") == ""


def test_logs_and_stdout_when_alias_invoked_from_sub_directory_with_verbose(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("subdir")
    os.mkdir(cwd)
    cmd = f"../pw -vv combine-pw-scripts"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env)

    assert not proc_result.returncode
    assert "< hi >" in proc_result.stdout.decode("utf-8")
    assert "< hello >" in proc_result.stdout.decode("utf-8")
    assert "creating pyprojectx venv in" in proc_result.stderr.decode("utf-8")
    assert "INFO:pyprojectx.log:Running command in IsolatedVirtualEnv: pycowsay hi" in proc_result.stderr.decode(
        "utf-8"
    )
    assert (
        "DEBUG:pyprojectx.log:Running tool command in virtual environment, tool: pycowsay, full command: pycowsay hello"
        in proc_result.stderr.decode("utf-8")
    )


def test_output_with_errors(tmp_project):
    project_dir, env = tmp_project
    pw_cmd = "pw" if sys.platform == "win32" else "./pw"
    cmd = f"{pw_cmd} -q failing-install"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env)

    assert proc_result.returncode == 1
    assert proc_result.stdout.decode("utf-8") == ""
    assert "PYPROJECTX ERROR: installation of 'failing-install' failed with exit code" in proc_result.stderr.decode(
        "utf-8"
    )

    cmd = f"{pw_cmd} -q failing-shell"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env)

    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8") == ""
    assert "go-foo-bar" in proc_result.stderr.decode("utf-8")

    cmd = f"{pw_cmd} -q foo-bar"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env)

    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8") == ""
    assert f"'foo-bar' is not configured as pyprojectx tool or alias in" in proc_result.stderr.decode("utf-8")
