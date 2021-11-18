import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from packaging.version import Version

import pyprojectx.env
from pyprojectx.env import IsolatedVirtualEnv


@pytest.fixture
def tmp_dir():
    path = tempfile.mkdtemp(prefix="px-home-")
    yield path
    shutil.rmtree(path)


def test_isolated_env_path(tmp_dir):
    # TODO test  poetry run python -c print("hello world!")
    # TODO test that  poetry version > file does not include logging
    # TODO test virtualenv install requirements failures
    # TODO set virtualenv verbosity to verbosity - 1
    # TODO pw should omit internal stacktrace when cmd fails f.e. ./pw virtualenv -foo
    pass
