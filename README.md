![pyprojectx](https://pyprojectx.github.io/assets/px.png)

# Pyprojectx: All-inclusive Python Projects

Execute scripts from pyproject.toml, installing tools on-the-fly

## [Full documentation](https://pyprojectx.github.io)

## Introduction
Pyprojectx makes it easy to create all-inclusive Python projects; no need to install any tools upfront,
not even Pyprojectx itself!

Tools that are specified within your pyproject.toml file will be installed on demand when invoked from Pyprojectx:
```shell
> ./pw black src
Collecting black ...
Successfully installed black-23.9.1 ...

All done! ✨ 🍰 ✨
18 files left unchanged.
```

## Feature highlights
* Reproducible builds by treating tools and utilities as (locked) dev-dependencies
* No global installs, everything is stored inside your project directory (like npm's _node_modules_)
* Bootstrap your entire build process with a small wrapper script (like Gradle's _gradlew_ wrapper)
* Configure shortcuts for routine tasks
* Simple configuration in _pyproject.toml_

Projects can be build/tested/used immediately without explicit installation nor initialization:
```bash
git clone https://github.com/pyprojectx/px-demo.git
cd px-demo
./pw build
```
![Clone and Build](https://raw.githubusercontent.com/pyprojectx/pyprojectx/main/docs/docs/assets/build.png)

## Installation
One of the key features is that there is no need to install anything explicitly (except a Python 3.9+ interpreter).

`cd` into your project directory and download the
[wrapper scripts](https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip):

**Linux/Mac**
```bash
curl -LO https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip && unzip wrappers.zip && rm -f wrappers.zip
```

**Windows**
```powershell
Invoke-WebRequest https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip -OutFile wrappers.zip; Expand-Archive -Path wrappers.zip -DestinationPath .; Remove-Item -Path wrappers.zip
```

## Getting started
Initialize a new or existing project by adding tools (on Windows, replace `./pw` with `pw`):
```bash
./pw --add pdm,ruff,pre-commit,px-utils
./pw --install-context main
# invoke a tool via the wrapper script
./pw pdm --version
./pw ruff check src
# or activate the tool context
source .pyprojectx/main/activate
pdm --version
ruff check src
```

For reproducible builds and developer experience, it is recommended to lock the versions of the tools
and add the generated _pw.lock_ file to your repository:
```bash
./pw --lock
```

## Create command shortcuts
The _tool.pyprojectx.aliases_ section in _pyproject.toml_ can contain commandline aliases:
```toml
[tool.pyprojectx.aliases]
# convenience shortcuts
run = "poetry run"
test = "poetry run pytest"
lint = ["ruff check"]
check = ["@lint", "@test"]
```

## Usage
Instead of calling the CLI of a tool directly, prefix it with `./pw` (`pw` on Windows).

Examples:
```shell
./pw poetry add -D pytest
cd src
../pw lint
```

Aliases can be invoked as is or with extra arguments:
```shell
./pw poetry run my-script --foo bar
# same as above, but using the run alias
./pw run my-script --foo bar
```

## Why yet another tool?
* As Python noob I had hard times setting up a project and building existing projects
* There is always someone in the team having issues with his setup, either with a specific tool, with Homebrew, pipx, ...
* Using (PDM or Poetry) dev-dependencies to install tools, impacts your production dependencies and can even lead to dependency conflicts
* Different projects often require different versions of the same tool

## Example projects
* This project (using PDM)
* [px-demo](https://github.com/pyprojectx/px-demo) (using PDM)

## Development
* Build/test:
```shell
git clone https://github.com/pyprojectx/pyprojectx.git
cd pyprojectx
./pw build
```

* Use your local pyprojectx copy in another project: set the path to pyprojectx in the _PYPROJECTX_PACKAGE_ environment variable
  and create a symlink to the wrapper script.
```shell
# Linux, Mac
export PYPROJECTX_PACKAGE=path/to/pyprojectx
ln -s $PYPROJECTX_PACKAGE/src/pyprojectx/wrapper/pw.py pw
# windows
set PYPROJECTX_PACKAGE=path/to/pyprojectx
mklink pw %PYPROJECTX_PACKAGE%\src\pyprojectx\wrapper\pw.py
# or copy the wrapper script if you can't create a symlink on windows
copy %PYPROJECTX_PACKAGE%\src\pyprojectx\wrapper\pw.py pw
```
