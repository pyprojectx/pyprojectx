from pyprojectx.config import Config
from pyprojectx.env import IsolatedVirtualEnv
from pyprojectx.hash import calculate_hash
from pyprojectx.lock import can_lock, get_or_update_locked_requirements


def test_can_lock():
    assert can_lock({"requirements": ["my-package==1.0.0"]})
    assert not can_lock({"requirements": ["my-package==1.0.0", "-e ."]})
    assert not can_lock({"requirements": ["my-package==1.0.0", "--editable ."]})


def test_up_to_date_lock_keeps_original_requirements_hash(tmp_dir):
    toml = tmp_dir / "pyproject.toml"
    toml.write_text('[tool.pyprojectx]\nmain = ["pkg==1.0"]\n', encoding="utf-8")
    config = Config(toml)
    original = config.get_requirements("main")
    original_hash = calculate_hash(original)
    locked_packages = ["dep==2.0", "pkg==1.0.0"]
    config.lock_file.write_text(
        f'[main]\nhash = "{original_hash}"\nrequirements = {locked_packages}\n',
        encoding="utf-8",
    )

    result, modified = get_or_update_locked_requirements("main", config, quiet=True)

    assert modified is False
    assert result["hash"] == original_hash
    assert result["requirements"] == locked_packages

    env = IsolatedVirtualEnv(tmp_dir / "venvs", "main", result)
    locked_hash = calculate_hash({**original, "requirements": locked_packages})
    assert original_hash in str(env.path)
    assert locked_hash not in str(env.path)
