import shutil
import subprocess
import sys
from pathlib import Path

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
    process = subprocess.run(
        cmd + " skip-path", shell=True, cwd=cwd, env=env, check=True, capture_output=True, text=True
    )

    px_dir = cwd.joinpath(".pyprojectx")
    assert px_dir.joinpath("global", "pw").exists()
    assert px_dir.joinpath("px").exists()
    assert px_dir.joinpath("pxg").exists()
    assert px_dir.joinpath("px.bat").exists()
    assert px_dir.joinpath("pxg.bat").exists()
    with px_dir.joinpath("global", "pyproject.toml").open("r") as f:
        toml_content = str(f.read())
        assert toml_content.startswith('[tool.pyprojectx]\ncwd = "."\n')
        assert "[tool.pyprojectx.aliases]" in toml_content
    assert "Global Pyprojectx scripts are installed in your home directory." in process.stderr
    assert "Created a global pyproject.toml file" in process.stderr

    # should not overwrite existing pyproject.toml
    process = subprocess.run(cmd, shell=True, cwd=cwd, env=env, check=True, capture_output=True, text=True)
    assert "Global Pyprojectx scripts are installed in your home directory." in process.stderr
    assert "Created a global pyproject.toml file" not in process.stderr


def copy_px(dir_name):
    dir_name.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent.parent / "../src/pyprojectx/wrapper/px", dir_name)
    shutil.copy(Path(__file__).parent.parent / "../src/pyprojectx/wrapper/px.bat", dir_name)
