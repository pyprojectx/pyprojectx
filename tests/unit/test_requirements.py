import sys

import pytest
from pyprojectx import requirements

PY_VER = f"py{sys.version_info.major}.{sys.version_info.minor}"


@pytest.mark.parametrize(
    ("requirement_1", "requirement_2", "quiet", "ctx", "packages"),
    [
        ("my-package", "another-package", False, None, ["my-package", "another-package"]),
        ("my-package", "another-package", True, None, ["my-package", "another-package"]),
        ("my-package==x.y.z", "another-package", False, None, ["my-package==x.y.z", "another-package"]),
        ("main:my-package>x.y.z", "main:another-package", False, "main", ["my-package>x.y.z", "another-package"]),
        (
            "other-ctx:my-package~=x.y.z",
            "other-ctx:another-package , package-3==1.0.0",
            False,
            "other-ctx",
            ["my-package~=x.y.z", "another-package", "package-3==1.0.0"],
        ),
    ],
)
def test_add_requirement(tmp_dir, mocker, requirement_1, requirement_2, quiet, ctx, packages):  # noqa: PLR0913
    toml = tmp_dir / "pyproject.toml"
    assert not toml.exists()
    install_mock = mocker.patch("pyprojectx.env.IsolatedVirtualEnv.install")
    check_installable_mock = mocker.patch("pyprojectx.env.IsolatedVirtualEnv.check_is_installable")

    requirements.add_requirement(requirement_1, toml, tmp_dir / "venvs", quiet)

    assert toml.exists()
    assert toml.read_text() == f"[tool.pyprojectx]\n{ctx or 'main'} = [\"{packages[0]}\"]\n"
    install_mock.assert_called_with(quiet=quiet)
    run_args = ["pip", "install", packages[0], "--dry-run"]
    if quiet:
        run_args.append("--quiet")

    check_installable_mock.assert_called_with(packages[0:1], quiet)

    requirements.add_requirement(requirement_2, toml, tmp_dir / "venvs", quiet)

    toml_packages = '", "'.join(packages)
    assert toml.read_text() == f"[tool.pyprojectx]\n{ctx or 'main'} = [\"{toml_packages}\"]\n"
    install_mock.assert_called_with(quiet=quiet)
    run_args = ["pip", "install", *packages[1:], "--dry-run"]
    if quiet:
        run_args.append("--quiet")
    check_installable_mock.assert_called_with(packages[1:], quiet)
