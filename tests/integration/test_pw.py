import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import tomlkit

from pyprojectx.wrapper import pw

SCRIPT_PREFIX = ".\\" if sys.platform.startswith("win") else "./"
SCRIPT_SUFFIX = ".exe" if sys.platform.startswith("win") else ""

data_dir = Path(__file__).parent.parent / "data"


def test_install_ctx(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{SCRIPT_PREFIX}pw --install-context install-context"
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))
    assert "install-context-post-install" in proc_result.stdout.decode("utf-8")

    # check that symlinks to all installed tools are created in .pyprojectx/<ctx>
    pycowsay_script = Path(project_dir, f".pyprojectx/install-context/pycowsay{SCRIPT_SUFFIX}")
    assert pycowsay_script.exists()
    proc_result = subprocess.run(
        [pycowsay_script, "From symlink!"], capture_output=True, cwd=project_dir, env=env, check=False
    )
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))
    # check the powershell activation script
    if sys.platform.startswith("win"):
        activate_ps = Path(project_dir, ".pyprojectx/install-context/activate.ps1")
        assert activate_ps.exists()
        assert not activate_ps.is_symlink()
        assert activate_ps.read_text().startswith(". '")
        assert activate_ps.read_text().strip().endswith("Scripts\\activate.ps1'")


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
    if not sys.platform.startswith("win") and sys.version_info.minor < 12:
        assert not proc_result.stderr.decode("utf-8")

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
    if not sys.platform.startswith("win") and sys.version_info.minor < 12:
        assert not proc_result.stderr.decode("utf-8")

    cmd = f"{SCRIPT_PREFIX}pw -q pycow"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode
    assert "'pycow' is ambiguous" in proc_result.stderr.decode("utf-8")
    assert "pycowsay, pycowsay-hello, pycowsay-hi" in proc_result.stderr.decode("utf-8")
    if not sys.platform.startswith("win") and sys.version_info.minor < 12:
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
    if not sys.platform.startswith("win") and sys.version_info.minor < 12:
        assert not proc_result.stderr.decode("utf-8")

    cmd = f"{SCRIPT_PREFIX}pw -q list-files *.txt"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=True)
    assert sorted(proc_result.stdout.decode("utf-8").strip().split()) == [
        "post-install-file.txt",
        "pw-requirements.txt",
    ]


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
    "main": {"hash": "9a26a0b87d70275d42f57b40bc8ddfc3", "requirements": ["pycowsay==0.0.0.2"]},
    "tool-with-known-requirements": {
        "requirements": [
            "click==8.1.7",
            "colorama==0.4.6 ; platform_system == 'Windows'",
            "distlib==0.3.7",
            "filelock==3.13.1",
            "platformdirs==3.11.0",
            "pyprojectx==2.0.0",
            "tomlkit==0.12.3",
            "userpath==1.9.1",
            "virtualenv==20.24.6",
        ],
        "hash": "d38ebcc846fc99fe583218af16f35eb5",
        "post-install": "@post-install-action",
    },
}


def test_lock(tmp_lock_project):
    project_dir, env = tmp_lock_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    lock_file = project_dir / "pw.lock"
    assert not lock_file.exists()
    post_install_table_dir = project_dir / "post-install-table-dir"
    shutil.rmtree(post_install_table_dir, ignore_errors=True)

    cmd = f"{SCRIPT_PREFIX}pw --lock"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))

    assert lock_file.exists()
    lock_content = load_toml(lock_file)
    assert lock_content["main"] == locked_requirements["main"]
    assert lock_content["tool-with-known-requirements"] == locked_requirements["tool-with-known-requirements"]
    # check that the post-install script was run
    assert post_install_table_dir.exists()
    assert not list(Path(project_dir, ".pyprojectx/venvs").glob("no-lock*"))


def test_lock_python_version(tmp_lock_project):
    project_dir, env = tmp_lock_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    toml = project_dir / pw.PYPROJECT_TOML
    lock_python_version = data_dir / "lock_python_version.toml"
    shutil.copy(lock_python_version, toml)

    cmd = f"{SCRIPT_PREFIX}pw --lock"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode == 1
    assert "No solution found when resolving dependencies" in proc_result.stderr.decode("utf-8")


def test_automatic_lock_update(tmp_lock_project):
    project_dir, env = tmp_lock_project
    toml = data_dir / "test-lock.toml"
    shutil.copyfile(toml, project_dir / pw.PYPROJECT_TOML)
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    lock_file = project_dir / "pw.lock"
    outdated = data_dir / "outdated.lock"
    shutil.copy(outdated, lock_file)
    post_install_table_dir = project_dir / "post-install-table-dir"
    shutil.rmtree(post_install_table_dir, ignore_errors=True)

    cmd = f"{SCRIPT_PREFIX}pw -q show-version"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))

    assert proc_result.stdout.decode("utf-8").strip() == "2.0.0"
    error_output = proc_result.stderr.decode("utf-8")
    assert error_output.strip() == ""
    lock_content = load_toml(lock_file)
    assert lock_content["tool-with-known-requirements"] == locked_requirements["tool-with-known-requirements"]
    assert lock_content["main"] == locked_requirements["main"]
    # check that the post-install script was run
    assert Path(project_dir, "post-install-table-dir").exists()


def test_requirements_from_lock_are_used(tmp_lock_project):
    project_dir, env = tmp_lock_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()
    lock_file = project_dir / "pw.lock"
    test_lock_file = data_dir / "test-use-lock-requirements.lock"
    shutil.copy(test_lock_file, lock_file)
    for path in (project_dir / ".pyprojectx/venvs").glob("main*"):  # remove the tool contexts from other test runs
        shutil.rmtree(path)

    cmd = f"{SCRIPT_PREFIX}pw pycowsay --version"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))
    assert proc_result.stdout.decode("utf-8").strip() == "0.0.0.1"

    # when the lock file is modified, the modified requirements should be used
    test_lock_file = data_dir / "test-use-modified-lock-requirements.lock"
    shutil.copy(test_lock_file, lock_file)
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    if proc_result.returncode:
        print(proc_result.stderr.decode("utf-8"))
    assert proc_result.stdout.decode("utf-8").strip() == "0.0.0.2"


def test_shell(tmp_project):
    project_dir, env = tmp_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()

    cmd = f"{SCRIPT_PREFIX}pw -q echo-env-var"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    output = "windows-alias-var" if sys.platform.startswith("win") else "linux-alias-var"
    assert output in proc_result.stdout.decode("utf-8")
    assert not proc_result.stderr.decode("utf-8")


def test_venv_dir(tmp_project):
    project_dir, env = tmp_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()

    cmd = f"{SCRIPT_PREFIX}pw -q venv-pycowsay from-venv-dir"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert "from-venv-dir" in proc_result.stdout.decode("utf-8")
    assert Path(project_dir, ".venv").is_dir()


def test_add_package(tmp_project):
    project_dir, env = tmp_project
    assert Path(project_dir, f"{SCRIPT_PREFIX}pw").is_file()

    cmd = f'{SCRIPT_PREFIX}pw -q --add "pycowsay==0.0.0.2"'
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode == 0

    cmd = f"{SCRIPT_PREFIX}pw main-pycowsay-version"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode == 0
    assert proc_result.stdout.decode("utf-8").strip() == "0.0.0.2"


def test_default_tools(tmp_project):
    project_dir, env = tmp_project
    cmd = f"{SCRIPT_PREFIX}pw --toml no.toml uv --version"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=project_dir, env=env, check=False)
    assert proc_result.returncode == 0
    assert re.search(r"\d+.\d+.\d+", proc_result.stdout.decode("utf-8"))


def load_toml(path):
    with path.open() as f:
        return tomlkit.load(f)
