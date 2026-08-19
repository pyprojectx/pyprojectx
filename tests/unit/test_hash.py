from pyprojectx.hash import calculate_hash


def test_distinct_requirement_lists_do_not_collide():
    assert calculate_hash({"requirements": ["ab", "c"]}) != calculate_hash({"requirements": ["a", "bc"]})
    assert calculate_hash({"requirements": ["foo", "bar"]}) != calculate_hash({"requirements": ["foobar"]})


def test_requirements_and_post_install_do_not_collide():
    with_post_install = {"requirements": ["foo"], "post-install": "bar"}
    merged = {"requirements": ["foobar"]}
    assert calculate_hash(with_post_install) != calculate_hash(merged)


def test_requirement_order_does_not_change_hash():
    assert calculate_hash({"requirements": ["b", "a"]}) == calculate_hash({"requirements": ["a", "b"]})


def test_whitespace_is_stripped():
    assert calculate_hash({"requirements": ["  pkg==1.0  "]}) == calculate_hash({"requirements": ["pkg==1.0"]})


def test_empty_and_missing_requirements():
    assert calculate_hash({}) == calculate_hash({"requirements": []})
    assert calculate_hash({"requirements": [""]}) == calculate_hash({"requirements": []})
