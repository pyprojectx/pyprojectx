import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from pyprojectx.initializer.initializers import SCRIPT_EXTENSION, SCRIPT_PREFIX
from pyprojectx.wrapper.pw import PYPROJECT_TOML


def test_px_invoked_from_sub_directory(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("subdir")
    copy_px(cwd)

    cmd = f"{SCRIPT_PREFIX}px combine-pw-scripts"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)

    assert "< hello >" in proc_result.stdout.decode("utf-8")


def test_initialize_project(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("project")
    copy_px(cwd)

    cmd = f"{SCRIPT_PREFIX}px --init project"
    subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)

    assert cwd.joinpath(PYPROJECT_TOML).exists()
    assert cwd.joinpath("pw").exists()
    assert cwd.joinpath("pw.bat").exists()

    cmd = f"{SCRIPT_PREFIX}px -i -"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)
    assert set(proc_result.stdout.decode("utf-8").split()) == {"clean", "isort", "black"}
    assert "is not configured as tool or alias" in proc_result.stderr.decode("utf-8")


@pytest.mark.parametrize("tool", ["poetry", "pdm"])
def test_initialize_build_tool(tmp_project, tool):
    if os.environ.get("GITHUB_ACTIONS") and tool == "pdm" and sys.platform.startswith("win"):
        pytest.skip("skipping pdm init on windows in github workflow")

    project_dir, env = tmp_project
    cwd = project_dir.joinpath(tool)
    copy_px(cwd)

    cmd = f"{SCRIPT_PREFIX}px --verbose --verbose --init {tool} -n"
    subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)

    assert cwd.joinpath(PYPROJECT_TOML).exists()
    assert cwd.joinpath("pw").exists()
    assert cwd.joinpath("pw.bat").exists()

    aliases = ["install", "run", "outdated", "test", tool]

    cmd = f"{SCRIPT_PREFIX}px -i -"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)
    assert proc_result.stdout.decode("utf-8").strip().split() == aliases
    cmd = f"{SCRIPT_PREFIX}px -i install"
    proc_result = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd, env=env, check=True)
    assert "is an alias" in proc_result.stderr.decode("utf-8")
    assert proc_result.stdout.decode("utf-8").strip() == f"{tool} install"

    subprocess.run(f"{SCRIPT_PREFIX}px install", shell=True, capture_output=True, cwd=cwd, env=env, check=True)
    subprocess.run(f"{SCRIPT_PREFIX}px outdated", shell=True, capture_output=True, cwd=cwd, env=env, check=True)
    subprocess.run(
        f"{SCRIPT_PREFIX}px run python --version", shell=True, capture_output=True, cwd=cwd, env=env, check=True
    )
    proc_result = subprocess.run(
        f"{SCRIPT_PREFIX}px {tool} --version", shell=True, capture_output=True, cwd=cwd, env=env, check=False
    )
    version = re.search(r"(\d+\.)+(\d+)", proc_result.stdout.decode("utf-8"))[0]
    with cwd.joinpath(PYPROJECT_TOML).open() as f:
        assert f'{tool} = "{tool}=={version}"' in f.read()


def test_initialize_global(tmp_project):
    project_dir, env = tmp_project
    cwd = project_dir.joinpath("global")
    copy_px(cwd)
    env["PYPROJECTX_HOME_DIR"] = str(cwd)
    cmd = f"{SCRIPT_PREFIX}px --verbose --verbose --init global --skip-path"
    subprocess.run(cmd, shell=True, cwd=cwd, env=env, check=True)

    px_dir = cwd.joinpath(".pyprojectx")
    assert px_dir.joinpath("global", PYPROJECT_TOML).exists()
    assert px_dir.joinpath("global", "pw").exists()
    assert px_dir.joinpath(f"px{SCRIPT_EXTENSION}").exists()
    assert px_dir.joinpath(f"pxg{SCRIPT_EXTENSION}").exists()


def copy_px(dir_name):
    dir_name.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent.parent.joinpath(f"../src/pyprojectx/wrapper/px{SCRIPT_EXTENSION}"), dir_name)
