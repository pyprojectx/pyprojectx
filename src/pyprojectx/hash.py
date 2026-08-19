import hashlib

# Separate requirements from each other and from post-install so that
# ["ab", "c"] and ["a", "bc"], or requirements=["foo"] + post-install="bar"
# versus requirements=["foobar"], cannot produce the same digest.
_REQ_SEP = b"\x00"
_POST_INSTALL_SEP = b"\x01"


def calculate_hash(requirements_config: dict) -> str:
    md5 = hashlib.md5()
    requirements = requirements_config.get("requirements") or []
    for arg in sorted(req.strip() for req in requirements if req and req.strip()):
        md5.update(arg.encode())
        md5.update(_REQ_SEP)
    post_install = requirements_config.get("post-install")
    if post_install:
        md5.update(_POST_INSTALL_SEP)
        md5.update(post_install.strip().encode())
    return md5.hexdigest()
