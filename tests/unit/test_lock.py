from pyprojectx.lock import can_lock


def test_can_lock():
    assert can_lock({"requirements": ["my-package==1.0.0"]})
    assert not can_lock({"requirements": ["my-package==1.0.0", "-e ."]})
    assert not can_lock({"requirements": ["my-package==1.0.0", "--editable ."]})
