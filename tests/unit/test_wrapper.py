from pathlib import Path

from pyprojectx.wrapper import pw


def test_uv_posix_install_command_is_plain_curl():
    source = Path(pw.__file__).read_text(encoding="utf-8")
    assert "LsSf irm " not in source
    assert "uv-installer.sh | sh" in source
