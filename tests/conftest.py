import os
import shutil
import stat
import tempfile
from pathlib import Path

import pytest
from pyprojectx.wrapper import pw

data_dir = Path(__file__).with_name("data")


@pytest.fixture
def tmp_dir():
    path = tempfile.mkdtemp(prefix="build env")
    yield Path(path)
    shutil.rmtree(path)


def create_tmp_project(tmp_project_dir):
    shutil.copyfile(data_dir / "pw-test.toml", tmp_project_dir / pw.PYPROJECT_TOML)
    shutil.copy(data_dir / "pw-requirements.txt", tmp_project_dir)
    pw_copy = Path(tmp_project_dir, "pw")
    pyprojectx_project_dir = Path(__file__).parent.parent
    shutil.copyfile(pyprojectx_project_dir / "src/pyprojectx/wrapper/pw.py", pw_copy)
    pw_copy.chmod(stat.S_IRWXU | stat.S_IRWXG)
    shutil.copy(pyprojectx_project_dir / "src/pyprojectx/wrapper/pw.bat", tmp_project_dir)
    shutil.copytree(data_dir / "bin", tmp_project_dir / "bin")
    env = os.environ.copy()
    env["PYPROJECTX_PACKAGE"] = str(pyprojectx_project_dir.absolute())
    return tmp_project_dir, env


@pytest.fixture(scope="session")
def tmp_project(tmp_path_factory):
    tmp_project_dir, env = create_tmp_project(tmp_path_factory.mktemp("project dir"))
    return tmp_project_dir, env


@pytest.fixture(scope="session")
def tmp_lock_project(tmp_path_factory):
    tmp_project_dir, env = create_tmp_project(tmp_path_factory.mktemp("lock dir"))
    toml = data_dir / "test-lock.toml"
    shutil.copyfile(toml, tmp_project_dir / pw.PYPROJECT_TOML)
    return tmp_project_dir, env
