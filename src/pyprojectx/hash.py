import hashlib


def calculate_hash(requirements_config: dict) -> str:
    md5 = hashlib.md5()
    for arg in [*requirements_config.get("requirements", []), requirements_config.get("post-install")]:
        if arg:
            md5.update(arg.strip().encode())
    return md5.hexdigest()
