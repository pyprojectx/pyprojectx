import os
import re
import subprocess
import sys
from pathlib import Path

from pyprojectx.initializer.initializers import SCRIPT_PREFIX

# pylint: disable=redefined-outer-name


def test_logs_and_stdout_with_quiet(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{SCRIPT_PREFIX}pw -q pycowsay Hello px!"
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
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

    cmd = f"{SCRIPT_PREFIX}pw -q list-files *.toml"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert proc_result.stdout.decode("utf-8").strip() == "pyproject.toml"


def test_logs_and_stdout_when_alias_invoked_from_sub_directory_with_verbose(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("subdir")
    os.makedirs(cwd, exist_ok=True)
    cmd = f"..{os.sep}pw -vv combine-pw-scripts"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)

    assert "< hi >" in proc_result.stdout.decode("utf-8")
    assert "< hello >" in proc_result.stdout.decode("utf-8")
    assert "INFO:pyprojectx.log:Running command in isolated venv pycowsay: pycowsay hi" in proc_result.stderr.decode(
        "utf-8"
    )
    assert (
        "DEBUG:pyprojectx.log:Running tool command in virtual environment, tool: pycowsay, full command: pycowsay hello"
        in proc_result.stderr.decode("utf-8")
    )


def test_alias_abbreviations(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{SCRIPT_PREFIX}pw -q pHe"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert "< hello >" in proc_result.stdout.decode("utf-8")
    if not sys.platform.startswith("win"):
        assert proc_result.stderr.decode("utf-8") == ""

    cmd = f"{SCRIPT_PREFIX}pw -q pycow"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode
    assert "'pycow' is ambiguous" in proc_result.stderr.decode("utf-8")
    assert "pycowsay, pycowsay-hi, pycowsay-hello" in proc_result.stderr.decode("utf-8")
    if not sys.platform.startswith("win"):
        assert proc_result.stdout.decode("utf-8") == ""


def test_output_with_errors(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{SCRIPT_PREFIX}pw -q failing-install"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)

    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8") == ""
    assert "PYPROJECTX ERROR: installation of 'failing-install' failed with exit code" in proc_result.stderr.decode(
        "utf-8"
    )

    cmd = f"{SCRIPT_PREFIX}pw -q failing-shell"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)

    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8") == ""
    assert "go-foo-bar" in proc_result.stderr.decode("utf-8")

    cmd = f"{SCRIPT_PREFIX}pw -q foo-bar"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)

    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8") == ""
    stderr = proc_result.stderr.decode("utf-8")
    assert re.search("foo-bar.+is not configured as tool or alias in.+pyproject.toml", stderr)
