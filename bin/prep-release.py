import os
import re
from pathlib import Path
from zipfile import ZipFile

# extract version from tag
RELEASE_VERSION = os.environ["GITHUB_REF_NAME"]

# cleanup old files
Path("wrappers.zip").unlink(missing_ok=True)
Path(".changelog.md").unlink(missing_ok=True)

# replace __version__ in wrapper and pyproject.toml
pw = Path("src/pyprojectx/wrapper/pw.py")
pw.write_text(pw.read_text().replace("__version__", RELEASE_VERSION))
pyproject = Path("pyproject.toml")
pyproject_content = re.sub(r'version\s*=\s*"\d.\d.\d.dev"', f'version = "{RELEASE_VERSION}"', pyproject.read_text())
pyproject.write_text(pyproject_content)

# create the distribution zip
with ZipFile("wrappers.zip", "w") as zip_file:
    zip_file.write("src/pyprojectx/wrapper/pw.py", "pw")
    zip_file.write("src/pyprojectx/wrapper/pw.bat", "pw.bat")

# extract the first change log from CHANGELOG.md
with Path("CHANGELOG.md").open() as changelog, Path(".changelog.md").open("w") as out:
    fist_header = False
    for line in changelog.readlines():
        if not fist_header:
            if line.startswith("###"):
                fist_header = True
            else:
                continue
        if fist_header and line.startswith("Release"):
            break
        out.write(line)
