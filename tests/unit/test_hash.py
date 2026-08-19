from pyprojectx.hash import calculate_hash


def test_hash_is_stable():
    """Pin the algorithm: changing it invalidates every venv path and pw.lock entry in the wild.

    Update these values only together with a deliberate, documented hash change.
    """
    assert calculate_hash({"requirements": ["req1", "req2"]}) == "e5993ae7c002fdae15e39e1e7f07bca6"
    assert calculate_hash({"requirements": ["pkg==1.0"], "post-install": "echo hi"}) == (
        "cefcedb0a2479d3c65b60a8ba33e8c39"
    )


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
