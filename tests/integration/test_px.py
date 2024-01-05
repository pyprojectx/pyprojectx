import shutil
import subprocess
import sys
from pathlib import Path

from pyprojectx.install_global import SCRIPT_EXTENSION

SCRIPT_PREFIX = ".\\" if sys.platform.startswith("win") else "./"


def test_px_invoked_from_sub_directory(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("subdir")
    copy_px(cwd)

    cmd = f"{SCRIPT_PREFIX}px combine-pw-scripts"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)

    assert "< hello >" in proc_result.stdout.decode("utf-8")


def test_install_px(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("global")
    copy_px(cwd)
    env["PYPROJECTX_HOME_DIR"] = str(cwd)
    cmd = f"{SCRIPT_PREFIX}px --verbose --verbose --install-px"
    subprocess.run(cmd + " skip-path", shell=True, cwd=cwd, env=env, check=True)

    px_dir = cwd.joinpath(".pyprojectx")
    assert px_dir.joinpath("global", "pw").exists()
    assert px_dir.joinpath(f"px{SCRIPT_EXTENSION}").exists()
    assert px_dir.joinpath(f"pxg{SCRIPT_EXTENSION}").exists()

    # installing again should fail
    process = subprocess.run(cmd, shell=True, cwd=cwd, env=env, check=False, capture_output=True, text=True)
    assert process.returncode == 1
    assert "already exists, use '--install-px --force-install' to overwrite" in process.stderr

    # installing again with force should succeed
    process = subprocess.run(
        cmd + " --force-install skip-path", shell=True, cwd=cwd, env=env, check=True, capture_output=True, text=True
    )
    assert "Global Pyprojectx scripts are installed in your home directory." in process.stderr


def copy_px(dir_name):
    dir_name.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent.parent.joinpath(f"../src/pyprojectx/wrapper/px{SCRIPT_EXTENSION}"), dir_name)
