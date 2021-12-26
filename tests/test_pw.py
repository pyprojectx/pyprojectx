import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from pyprojectx.wrapper import pw

# pylint: disable=redefined-outer-name

PW_CMD = ".\\pw" if sys.platform.startswith("win") else "./pw"


@pytest.fixture
def tmp_project(tmp_dir):
    toml = Path(__file__).with_name("data").joinpath("pw-test.toml")
    shutil.copyfile(toml, tmp_dir.joinpath(pw.PYPROJECT_TOML))
    pw_copy = Path(tmp_dir, "pw")
    pyprojectx_package = toml.parent.joinpath("../..")
    shutil.copyfile(pyprojectx_package.joinpath("src/pyprojectx/wrapper/pw.py"), pw_copy)
    os.chmod(pw_copy, stat.S_IRWXU | stat.S_IRWXG)
    shutil.copy(pyprojectx_package.joinpath("src/pyprojectx/wrapper/pw.bat"), tmp_dir)
    env = os.environ.copy()
    env["PYPROJECTX_PACKAGE"] = str(pyprojectx_package.absolute())
    return tmp_dir, env


def test_logs_and_stdout_with_quiet(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{PW_CMD} -q pycowsay Hello px!"
    assert Path(project_dir, PW_CMD).is_file()
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)

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

""".replace(
            "\n", os.linesep
        )
    )
    if not sys.platform.startswith("win"):
        assert proc_result.stderr.decode("utf-8") == ""

    cmd = f"{PW_CMD} -q list-files *.toml"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert proc_result.stdout.decode("utf-8").strip() == "pyproject.toml"


def test_logs_and_stdout_when_alias_invoked_from_sub_directory_with_verbose(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("subdir")
    os.mkdir(cwd)
    cmd = f"..{os.sep}{PW_CMD} -vv combine-pw-scripts"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)

    assert "< hi >" in proc_result.stdout.decode("utf-8")
    assert "< hello >" in proc_result.stdout.decode("utf-8")
    assert "creating pyprojectx venv in" in proc_result.stderr.decode("utf-8")
    assert "INFO:pyprojectx.log:Running command in isolated venv pycowsay: pycowsay hi" in proc_result.stderr.decode(
        "utf-8"
    )
    assert (
        "DEBUG:pyprojectx.log:Running tool command in virtual environment, tool: pycowsay, full command: pycowsay hello"
        in proc_result.stderr.decode("utf-8")
    )


def test_output_with_errors(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{PW_CMD} -q failing-install"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)

    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8") == ""
    assert "PYPROJECTX ERROR: installation of 'failing-install' failed with exit code" in proc_result.stderr.decode(
        "utf-8"
    )

    cmd = f"{PW_CMD} -q failing-shell"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)

    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8") == ""
    assert "go-foo-bar" in proc_result.stderr.decode("utf-8")

    cmd = f"{PW_CMD} -q foo-bar"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)

    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8") == ""
    assert "'foo-bar' is not configured as pyprojectx tool or alias in" in proc_result.stderr.decode("utf-8")


@pytest.mark.skipif(sys.platform.startswith("win"), reason="linux only")
def test_linux_px_invoked_from_sub_directory_with_verbose(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("subdir")
    os.mkdir(cwd)
    shutil.copy(Path(__file__).parent.joinpath("../src/pyprojectx/wrapper/px"), cwd)

    cmd = "./px combine-pw-scripts"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)

    assert "< hello >" in proc_result.stdout.decode("utf-8")
