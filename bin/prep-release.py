import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZipFile

import tomlkit


def main(release_version):
    cleanup_old_files()
    final_release = re.match(r"^\d+.\d+.\d+$", release_version)
    replace_version_in_files(release_version)
    if final_release:
        generate_release_changelog()
        zip_wrappers()
        update_changelog(release_version)
    subprocess.run(["git", "tag", "-am", f"Release {release_version} by Github action", release_version], check=True)


def cleanup_old_files():
    Path("wrappers.zip").unlink(missing_ok=True)
    Path(".release-changelog.md").unlink(missing_ok=True)


def replace_version_in_files(release_version):
    pyproject = Path("pyproject.toml")
    with pyproject.open("rb") as f:
        pyproject_dict = tomlkit.load(f)
        uv_version = next(i for i in pyproject_dict["project"]["dependencies"] if i.startswith("uv")).split("==")[1]

    # replace __version__ in wrapper and pyproject.toml
    pw = Path("src/pyprojectx/wrapper/pw.py")
    pw.write_text(pw.read_text().replace("__version__", release_version).replace("__uv_version__", uv_version))
    pyproject_content = re.sub(r'version\s*=\s*"\d.\d.\d.dev"', f'version = "{release_version}"', pyproject.read_text())
    pyproject.write_text(pyproject_content)


def zip_wrappers():
    with ZipFile("wrappers.zip", "w") as zip_file:
        zip_file.write("src/pyprojectx/wrapper/pw.py", "pw")
        zip_file.write("src/pyprojectx/wrapper/pw.bat", "pw.bat")


def generate_release_changelog():
    # extract the first change log from CHANGELOG.md
    with Path("CHANGELOG.md").open() as changelog, Path(".release-changelog.md").open("w") as out:
        for index, line in enumerate(changelog):
            if index == 0 and not line.startswith("### "):
                message = (
                    "First line of CHANGELOG.md must start with '### '. Did you forget to add a new release notes?"
                )
                raise RuntimeError(message)
            if line.startswith("Release"):
                break
            out.write(line)


def update_changelog(release_version):
    date = datetime.now(tz=UTC).isoformat()[:10]
    with Path("CHANGELOG.md").open() as file:
        original_content = file.read()
    with Path("CHANGELOG.md").open("w") as file:
        file.write(f"Release v{release_version} ({date})\n")
        file.write("----------------------------\n")
        file.write(original_content)
    subprocess.run(["git", "add", "CHANGELOG.md"], check=True)
    subprocess.run(["git", "commit", "-m", f"Release v{release_version}"], check=True)


if __name__ == "__main__":
    main(sys.argv[1])
