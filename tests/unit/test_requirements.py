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
    assert toml.read_text() == f'[tool.pyprojectx]\n{ctx or "main"} = ["{packages[0]}"]\n'
    install_mock.assert_called_with(quiet=quiet)
    run_args = ["pip", "install", packages[0], "--dry-run"]
    if quiet:
        run_args.append("--quiet")

    check_installable_mock.assert_called_with(packages[0:1], quiet)

    requirements.add_requirement(requirement_2, toml, tmp_dir / "venvs", quiet)

    toml_packages = '", "'.join(packages)
    assert toml.read_text() == f'[tool.pyprojectx]\n{ctx or "main"} = ["{toml_packages}"]\n'
    install_mock.assert_called_with(quiet=quiet)
    run_args = ["pip", "install", *packages[1:], "--dry-run"]
    if quiet:
        run_args.append("--quiet")
    check_installable_mock.assert_called_with(packages[1:], quiet)


def test_add_vcs_url_uses_main_context(tmp_dir, mocker):
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.install")
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.check_is_installable")
    toml = tmp_dir / "pyproject.toml"
    url = "git+https://github.com/foo/bar.git"
    requirements.add_requirement(url, toml, tmp_dir / "venvs", True)
    assert toml.read_text() == f'[tool.pyprojectx]\nmain = ["{url}"]\n'


def test_add_file_url_uses_main_context(tmp_dir, mocker):
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.install")
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.check_is_installable")
    toml = tmp_dir / "pyproject.toml"
    url = "file:///tmp/mypkg"
    requirements.add_requirement(url, toml, tmp_dir / "venvs", True)
    assert toml.read_text() == f'[tool.pyprojectx]\nmain = ["{url}"]\n'


def test_add_vcs_url_with_explicit_context(tmp_dir, mocker):
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.install")
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.check_is_installable")
    toml = tmp_dir / "pyproject.toml"
    url = "git+https://github.com/foo/bar.git"
    requirements.add_requirement(f"tools:{url}", toml, tmp_dir / "venvs", True)
    assert toml.read_text() == f'[tool.pyprojectx]\ntools = ["{url}"]\n'


def test_add_does_not_treat_package_prefix_as_duplicate(tmp_dir, mocker):
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.install")
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.check_is_installable")
    toml = tmp_dir / "pyproject.toml"
    requirements.add_requirement("uvloop", toml, tmp_dir / "venvs", True)
    requirements.add_requirement("uv", toml, tmp_dir / "venvs", True)
    assert toml.read_text() == '[tool.pyprojectx]\nmain = ["uvloop", "uv"]\n'


def test_add_detects_same_package_name(tmp_dir, mocker):
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.install")
    mocker.patch("pyprojectx.env.IsolatedVirtualEnv.check_is_installable")
    toml = tmp_dir / "pyproject.toml"
    requirements.add_requirement("My-Package", toml, tmp_dir / "venvs", True)
    with pytest.raises(Warning, match="my-package is already a requirement"):
        requirements.add_requirement("my_package==1.0", toml, tmp_dir / "venvs", True)
