import sys

import pytest
from pyprojectx import requirements
from pyprojectx.hash import calculate_hash

PY_VER = f"py{sys.version_info.major}.{sys.version_info.minor}"


@pytest.mark.parametrize(
    ("package", "quiet", "ctx", "package_2"),
    [
        ("my-package", False, None, "another-package"),
        ("my-package", True, None, "another-package"),
        ("my-package==x.y.z", False, None, "another-package"),
        ("my-package>x.y.z", False, "main", "another-package"),
        ("my-package~=x.y.z", False, "other-ctx", "another-package"),
    ],
)
def test_add_requirement(tmp_dir, mocker, package, quiet, ctx, package_2):  # noqa: PLR0913
    package_prefix = f"{ctx}:" if ctx else ""
    toml = tmp_dir / "pyproject.toml"
    assert not toml.exists()
    install_mock = mocker.patch("pyprojectx.env.IsolatedVirtualEnv.install")
    run_mock = mocker.patch("pyprojectx.env.IsolatedVirtualEnv.run")

    requirements.add_requirement(f"{package_prefix}{package}", toml, tmp_dir / "venvs", quiet)

    assert toml.exists()
    assert toml.read_text() == f"[tool.pyprojectx]\n{ctx or 'main'} = [\"{package}\"]\n"
    install_mock.assert_called_with(quiet)
    run_args = ["pip", "install", package, "--dry-run"]
    if quiet:
        run_args.append("--quiet")

    hex_digest = calculate_hash({})
    run_mock.assert_called_with(run_args, env={}, cwd=tmp_dir / f"venvs/{ctx or 'main'}-{hex_digest}-{PY_VER}")

    requirements.add_requirement(f"{package_prefix}{package_2}", toml, tmp_dir / "venvs", quiet)

    assert toml.read_text() == f"[tool.pyprojectx]\n{ctx or 'main'} = [\"{package}\", \"{package_2}\"]\n"
    install_mock.assert_called_with(quiet)
    run_args = ["pip", "install", package_2, "--dry-run"]
    if quiet:
        run_args.append("--quiet")
    hex_digest = calculate_hash({"requirements": [package]})
    run_mock.assert_called_with(run_args, env={}, cwd=tmp_dir / f"venvs/{ctx or 'main'}-{hex_digest}-{PY_VER}")
