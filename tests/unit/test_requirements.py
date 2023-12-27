import sys
import pytest
from pyprojectx import requirements

PY_VER = f"py{sys.version_info.major}.{sys.version_info.minor}"


@pytest.mark.parametrize(
    ("package", "quiet", "ctx"),
    [
        ("my-package", False, None),
        ("my-package", True, None),
        ("my-package==x.y.z", False, None),
        ("my-package>x.y.z", False, "main"),
        ("my-package~=x.y.z", False, "other-ctx"),
    ],
)
def test_add_requirement_without_toml(tmp_dir, mocker, package, quiet, ctx):
    package_prefix = f"{ctx}:" if ctx else ""
    toml = tmp_dir / "pyproject.toml"
    install_mock = mocker.patch("pyprojectx.env.IsolatedVirtualEnv.install")
    run_mock = mocker.patch("pyprojectx.env.IsolatedVirtualEnv.run")

    requirements.add_requirement(f"{package_prefix}{package}", toml, tmp_dir / "venvs", quiet)

    assert toml.exists()
    assert toml.read_text() == f"[tool.pyprojectx]\n{ctx or 'main'} = [\"{package}\"]\n"
    install_mock.assert_called_with(quiet)
    run_args = ["pip", "install", package, "--dry-run"]
    if quiet:
        run_args.append("--quiet")
    run_mock.assert_called_with(
        run_args, env={}, cwd=tmp_dir / f"venvs/{ctx or 'main'}-d41d8cd98f00b204e9800998ecf8427e-{PY_VER}"
    )
