import re
from pathlib import Path

from pyprojectx.wrapper import pw

PROJECT_DIR = Path(__file__).parent.parent.parent
WRAPPER_DIR = PROJECT_DIR / "src" / "pyprojectx" / "wrapper"
# prep-release.py substitutes these placeholders, so the committed ./pw carries real versions
VERSION_LINE_RE = re.compile(r'^(VERSION|UV_VERSION) = ".*"$', re.MULTILINE)


def _without_versions(path: Path) -> str:
    return VERSION_LINE_RE.sub(r"\1", path.read_text(encoding="utf-8"))


def test_uv_posix_install_command_is_plain_curl():
    source = Path(pw.__file__).read_text(encoding="utf-8")
    assert "LsSf irm " not in source
    assert "uv-installer.sh | sh" in source


def test_committed_wrapper_is_in_sync_with_source():
    """The committed ./pw is a copy of the wrapper source with the versions filled in."""
    assert _without_versions(PROJECT_DIR / "pw") == _without_versions(WRAPPER_DIR / "pw.py")
    assert (PROJECT_DIR / "pw.bat").read_text(encoding="utf-8") == (WRAPPER_DIR / "pw.bat").read_text(encoding="utf-8")
