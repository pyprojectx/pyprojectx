import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

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


def test_download_falls_back_to_curl_when_urllib_has_no_ca_bundle(tmp_dir, mocker):
    """Interpreters without a CA bundle (f.i. a python.org macOS build) can't verify https with urllib."""
    urlretrieve_mock = mocker.patch("urllib.request.urlretrieve", side_effect=URLError("CERTIFICATE_VERIFY_FAILED"))
    run_mock = mocker.patch("subprocess.run")
    target = tmp_dir / "wrappers.zip"

    pw.download("https://example.com/wrappers.zip", target)

    urlretrieve_mock.assert_called_once_with("https://example.com/wrappers.zip", target)
    download_cmd = run_mock.call_args.args[0]
    assert not run_mock.call_args.kwargs.get("shell")
    assert download_cmd[0] == ("powershell" if sys.platform == "win32" else "curl")
    assert "https://example.com/wrappers.zip" in " ".join(download_cmd)
    assert str(target) in " ".join(download_cmd)


def test_download_quotes_a_target_path_containing_a_single_quote(tmp_dir, mocker):
    r"""Windows temp dirs embed the account name, so the path can contain a quote (f.i. C:\Users\O'Brien\...)."""
    mocker.patch("urllib.request.urlretrieve", side_effect=URLError("CERTIFICATE_VERIFY_FAILED"))
    run_mock = mocker.patch("subprocess.run")
    target = tmp_dir / "O'Brien" / "wrappers.zip"

    pw.download("https://example.com/wrappers.zip", target)

    download_cmd = run_mock.call_args.args[0]
    if sys.platform == "win32":
        # powershell escapes a single quote inside a single-quoted string by doubling it
        assert str(target).replace("'", "''") in download_cmd[-1]
    else:
        assert str(target) in download_cmd


def test_download_does_not_retry_an_http_error(tmp_dir, mocker):
    """The server answered, so the connection is fine and curl would only repeat the same status."""
    mocker.patch(
        "urllib.request.urlretrieve",
        side_effect=HTTPError("https://example.com/wrappers.zip", 404, "Not Found", {}, None),
    )
    run_mock = mocker.patch("subprocess.run")

    with pytest.raises(HTTPError):
        pw.download("https://example.com/wrappers.zip", tmp_dir / "wrappers.zip")

    run_mock.assert_not_called()


def test_committed_wrapper_is_in_sync_with_source():
    """The committed ./pw is a copy of the wrapper source with the versions filled in."""
    assert _without_versions(PROJECT_DIR / "pw") == _without_versions(WRAPPER_DIR / "pw.py")
    assert (PROJECT_DIR / "pw.bat").read_text(encoding="utf-8") == (WRAPPER_DIR / "pw.bat").read_text(encoding="utf-8")
