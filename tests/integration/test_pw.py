import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import tomlkit

SCRIPT_PREFIX = ".\\" if sys.platform.startswith("win") else "./"

pip_upgrade_regex = re.compile(r"\s*\[notice] A new release of pip.+upgrade pip\s*", re.DOTALL)
data_dir = Path(__file__).parent.parent / "data"


def test_install_ctx(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{SCRIPT_PREFIX}pw --install-context install-context"
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))
    assert "Successfully installed pycowsay-0.0.0.1" in proc_result.stderr.decode("utf-8")
    assert "install-context-post-install" in proc_result.stdout.decode("utf-8")


def test_logs_and_stdout_with_quiet(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{SCRIPT_PREFIX}pw -q pycowsay Hello px!"
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))

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

""".replace("\n", os.linesep)
    )
    if not sys.platform.startswith("win"):
        assert not pip_upgrade_regex.sub("", proc_result.stderr.decode("utf-8"))

    cmd = f"{SCRIPT_PREFIX}pw -q list-files *.toml"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))
    assert proc_result.stdout.decode("utf-8").strip() == "pyproject.toml"


@pytest.mark.parametrize("alias", ["combine-pw-scripts", "combine-pw-scripts-list"])
def test_logs_and_stdout_when_alias_invoked_from_sub_directory_with_verbose(alias, tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("subdir")
    cwd.mkdir(parents=True, exist_ok=True)
    cmd = f"..{os.sep}pw --verbose --verbose {alias}"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)

    assert "< hi >" in proc_result.stdout.decode("utf-8")
    assert "< hello >" in proc_result.stdout.decode("utf-8")
    assert "INFO:pyprojectx.log:Running command in isolated venv pycowsay: pycowsay hi" in proc_result.stderr.decode(
        "utf-8"
    )
    assert (
        "DEBUG:pyprojectx.log:Running command in virtual environment, ctx: pycowsay, full command: pycowsay hello"
        in proc_result.stderr.decode("utf-8")
    )
    assert (project_dir / "created-by-call-prm").exists()


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
    ("cmd", "stdout", "stderr"),
    [
        (
            f"{SCRIPT_PREFIX}pw -q failing-install",
            "",
            "PYPROJECTX ERROR: installation of 'failing-install' failed with exit code",
        ),
        (f"{SCRIPT_PREFIX}pw -q failing-shell", "", "go-foo-bar"),
        (
            f"{SCRIPT_PREFIX}pw",
            "",
            "usage: pyprojectx",
        ),
        (f"{SCRIPT_PREFIX}pw -q failing-list", "first-cmd-output-ok", "go-foo-bar"),
    ],
)
def test_output_with_errors(cmd, stdout, stderr, tmp_project):
    project_dir, env = tmp_project
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode
    assert proc_result.stdout.decode("utf-8").strip() == stdout
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

""".replace("\n", os.linesep)
    )
    if not sys.platform.startswith("win"):
        assert not pip_upgrade_regex.sub("", proc_result.stderr.decode("utf-8"))

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

""".replace("\n", os.linesep)
    )


def test_cwd(tmp_project):
    project_dir, env = tmp_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    cmd = f"{SCRIPT_PREFIX}pw -q ls-projectdir"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert "pw.bat" in proc_result.stdout.decode("utf-8")

    cmd = f"{SCRIPT_PREFIX}pw -q ls-pyprojectx"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert "pyprojectx" in proc_result.stdout.decode("utf-8")


def test_default_ctx(tmp_project):
    project_dir, env = tmp_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()

    cmd = f"{SCRIPT_PREFIX}pw -q ls-projectdir"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert "post-install-dir" in proc_result.stdout.decode(
        "utf-8"
    ), "the cmd did not run in the main ctx or the main post-install did not run"
    assert (project_dir / "post-install-dir").exists()

    cmd = f"{SCRIPT_PREFIX}pw -vvv pxrm post-install-dir"
    subprocess.run(cmd, shell=True, cwd=project_dir, env=env, check=True)
    assert not (project_dir / "post-install-dir").exists()


def test_run_script_with_args(tmp_project):
    project_dir, env = tmp_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()

    cmd = f"{SCRIPT_PREFIX}pw -vvv call-prm"
    subprocess.run(cmd, shell=True, cwd=project_dir, env=env, check=True)
    assert (project_dir / "created-by-call-prm").exists()


locked_requirements = {
    "main": {"hash": "0847ad891da4272b514080caa1eb825f", "requirements": ["px-utils==1.1.0"]},
    "tool-with-known-requirements": {
        "hash": "1af658158bd6e34e51157b81c6b3fdd5",
        "requirements": [
            "click==8.1.3",
            "colorama==0.4.6",
            "distlib==0.3.6",
            "filelock==3.11.0",
            "platformdirs==3.2.0",
            "pyprojectx==1.0.1",
            "tomli==2.0.1",
            "userpath==1.8.0",
            "virtualenv==20.23.0",
        ],
        "post-install": "pxmkdirs post-install-table-dir",
    },
}
if not sys.platform.startswith("win"):
    locked_requirements["tool-with-known-requirements"]["requirements"].remove("colorama==0.4.6")


def test_lock(tmp_lock_project):
    project_dir, env = tmp_lock_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    lock_file = project_dir / "pw.lock"
    assert not lock_file.exists()

    cmd = f"{SCRIPT_PREFIX}pw --lock"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))

    assert lock_file.exists()
    lock_content = load_toml(lock_file)
    assert lock_content["main"] == locked_requirements["main"]
    assert lock_content["tool-with-known-requirements"] == locked_requirements["tool-with-known-requirements"]


def test_automatic_lock_update(tmp_lock_project):
    project_dir, env = tmp_lock_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    lock_file = project_dir / "pw.lock"
    outdated = data_dir / "outdated.lock"
    shutil.copy(outdated, lock_file)

    cmd = f"{SCRIPT_PREFIX}pw -q show-version"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))

    assert proc_result.stdout.decode("utf-8").strip() == "1.0.1"
    error_output = proc_result.stderr.decode("utf-8")
    assert re.sub(r"\s*\[notice].*\n", "", error_output).strip() == ""
    lock_content = load_toml(lock_file)
    assert lock_content["tool-with-known-requirements"] == locked_requirements["tool-with-known-requirements"]
    assert not lock_content.get("main")

    cmd = f"{SCRIPT_PREFIX}pw pxrm foo/bar"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))
    assert "locking" in proc_result.stderr.decode("utf-8")
    # check that the post-install script was run
    assert Path(project_dir, "post-install-table-dir").exists()

    lock_content = load_toml(lock_file)
    assert lock_content["tool-with-known-requirements"] == locked_requirements["tool-with-known-requirements"]
    assert lock_content["main"] == locked_requirements["main"]

    # requirements with editable installs should not be locked
    cmd = f"{SCRIPT_PREFIX}pw -q no-lock-cmd"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    print(proc_result.stderr.decode("utf-8"))
    assert "invoked no-lock" in proc_result.stdout.decode("utf-8")
    assert not lock_content.get("no-lock")


def test_requirements_from_lock_are_used(tmp_lock_project):
    project_dir, env = tmp_lock_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    lock_file = project_dir / "pw.lock"
    test_lock_file = data_dir / "test-use-lock-requirements.lock"
    shutil.copy(test_lock_file, lock_file)
    for path in (project_dir / ".pyprojectx/venvs/main").glob("main*"):
        shutil.rmtree(path)

    cmd = f"{SCRIPT_PREFIX}pw prm foo/bar"  # lock file has px-utils==1.0.0 which uses prm instead of pxrm
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))

    assert not proc_result.returncode


def test_shell(tmp_project):
    project_dir, env = tmp_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()

    cmd = f"{SCRIPT_PREFIX}pw -q echo-env-var"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    output = "windows-alias-var" if sys.platform.startswith("win") else "linux-alias-var"
    assert output in proc_result.stdout.decode("utf-8")
    assert not proc_result.stderr.decode("utf-8")


def load_toml(path):
    with path.open() as f:
        return tomlkit.load(f)
