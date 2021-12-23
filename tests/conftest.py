import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir():
    path = tempfile.mkdtemp(prefix="build-env-")
    yield Path(path)
    shutil.rmtree(path)
