import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from pyprojectx.initializer.initializers import SCRIPT_PREFIX


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
        assert not proc_result.stderr.decode("utf-8")

    cmd = f"{SCRIPT_PREFIX}pw -q list-files *.toml"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert proc_result.stdout.decode("utf-8").strip() == "pyproject.toml"


def test_logs_and_stdout_when_alias_invoked_from_sub_directory_with_verbose(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("subdir")
    cwd.mkdir(parents=True, exist_ok=True)
    cmd = f"..{os.sep}pw --verbose --verbose combine-pw-scripts"
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
        assert not proc_result.stderr.decode("utf-8")

    cmd = f"{SCRIPT_PREFIX}pw -q pycow"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode
    assert "'pycow' is ambiguous" in proc_result.stderr.decode("utf-8")
    assert "pycowsay, pycowsay-hi, pycowsay-hello" in proc_result.stderr.decode("utf-8")
    if not sys.platform.startswith("win"):
        assert not proc_result.stdout.decode("utf-8")


@pytest.mark.parametrize(
    ("cmd", "stderr"),
    [
        (
            f"{SCRIPT_PREFIX}pw -q failing-install",
            "PYPROJECTX ERROR: installation of 'failing-install' failed with exit code",
        ),
        (f"{SCRIPT_PREFIX}pw -q failing-shell", "go-foo-bar"),
        (f"{SCRIPT_PREFIX}pw -q foo-bar", "foo-bar.+is not configured as tool or alias in.+pyproject.toml"),
        (
            f"{SCRIPT_PREFIX}pw",
            "usage: pyprojectx",
        ),
    ],
)
def test_output_with_errors(cmd, stderr, tmp_project):
    project_dir, env = tmp_project
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode
    assert not proc_result.stdout.decode("utf-8")
    assert re.search(stderr, proc_result.stderr.decode("utf-8"))


def test_post_install(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{SCRIPT_PREFIX}pw -q say-post-install"
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)

    assert (
        proc_result.stdout.decode("utf-8")
        == """
  -------------------
< post-install-action >
  -------------------
   \\   ^__^
    \\  (oo)\\_______
       (__)\\       )\\/\\
           ||----w |
           ||     ||


  ------------------
< after-post-install >
  ------------------
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
        assert not proc_result.stderr.decode("utf-8")

    cmd = f"{SCRIPT_PREFIX}pw -q list-files *.txt"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert proc_result.stdout.decode("utf-8").strip() == "post-install-file.txt"


def test_alias_with_quoted_args(tmp_project):
    project_dir, env = tmp_project
    cmd = f'{SCRIPT_PREFIX}pw -q pycowsay "quoted    arguments are preserved"'
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)

    assert (
        proc_result.stdout.decode("utf-8")
        == """
  ---------------------------------
< quoted    arguments are preserved >
  ---------------------------------
   \\   ^__^
    \\  (oo)\\_______
       (__)\\       )\\/\\
           ||----w |
           ||     ||

""".replace(
            "\n", os.linesep
        )
    )
