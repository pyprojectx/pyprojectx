import os
import shutil
import stat
import tempfile
from pathlib import Path

import pytest

from pyprojectx.wrapper import pw


@pytest.fixture()
def tmp_dir():
    path = tempfile.mkdtemp(prefix="build-env-")
    yield Path(path)
    shutil.rmtree(path)


@pytest.fixture(scope="session")
def tmp_project():
    tmp = Path(tempfile.mkdtemp(prefix="build-env-"))
    toml = Path(__file__).with_name("data").joinpath("pw-test.toml")
    shutil.copyfile(toml, tmp.joinpath(pw.PYPROJECT_TOML))
    pw_copy = Path(tmp, "pw")
    project_dir = Path(__file__).parent.parent
    shutil.copyfile(project_dir.joinpath("src/pyprojectx/wrapper/pw.py"), pw_copy)
    pw_copy.chmod(stat.S_IRWXU | stat.S_IRWXG)
    shutil.copy(project_dir.joinpath("src/pyprojectx/wrapper/pw.bat"), tmp)
    env = os.environ.copy()
    env["PYPROJECTX_PACKAGE"] = str(project_dir.absolute())
    yield tmp, env
    shutil.rmtree(tmp)
