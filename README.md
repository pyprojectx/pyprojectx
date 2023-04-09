![pyprojectx](docs/docs/assets/px.png)

# Pyprojectx: All-inclusive Python Projects

Execute scripts from pyproject.toml, installing tools on-the-fly

## [Full documentation](https://pyprojectx.github.io)

## Introduction
Pyprojectx makes it easy to create all-inclusive Python projects; no need to install any tools upfront,
not even Pyprojectx itself!

## Feature highlights
* Reproducible builds by treating tools and utilities as (versioned) dev-dependencies
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
One of the key features is that there is no need to install anything explicitly (except a Python 3.7+ interpreter).

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

## Project initialization
Initialize a new or existing project with the _--init_ option (on Windows, replace `./pw` with `pw`):
* `./pw --init project`: add pyprojectx example sections to an existing or new _pyproject.toml_ in the current directory.
* `./pw --init pdm`: initialize a [PDM](https://pdm.fming.dev/) project and add pyprojectx example sections to _pyproject.toml_.
* `./pw --init poetry`: initialize a [Poetry](https://python-poetry.org/) project and add pyprojectx example sections to _pyproject.toml_.

## Configuration
Add the _tool.pyprojectx_ section inside _pyproject.toml_ in your project's root directory.

Each entry has the form `tool = "pip-requirements"`, where _pip-requirements_ adheres to the
[requirements file format](https://pip.pypa.io/en/stable/reference/requirements-file-format/).

Example:
```toml
[tool.pyprojectx]
# require a specific poetry version
poetry = "poetry==1.1.13"
# use the latest black
isort = "isort"
# install flake8 in combination with plugins
flake8 = ["flake8", "flake8-black"]
```

The _tool.pyprojectx.aliases_ section can contain optional commandline aliases in the form

`alias = [@tool_key:] command`

Example:
```toml
[tool.pyprojectx.aliases]
# convenience shortcuts
run = "poetry run"
test = "poetry run pytest"

# flake8-black also contains the black script
black = "@flake8: black"

# simple shell commands
clean = "rm -f .coverage .pytest_cache"

# when running an alias from within another alias, prefix it with `pw@`
check = "pw@flake8 && pw@test"
```

## Usage
Instead of calling the commandline of a tool directly, prefix it with `path\to\pw`.

Examples:
```shell
./pw poetry add -D pytest
cd src
../pw black *.py
```

... or on Windows:
```shell
pw poetry add -D pytest
cd src
..\pw black *.py
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
* This project (using Poetry)
* [px-demo](https://github.com/pyprojectx/px-demo) (using PDM)

## Development
* Build/test:
```shell
git clone https://github.com/pyprojectx/pyprojectx.git
cd pyprojectx
./pw build
```

* Set the path to pyprojectx in the _PYPROJECTX_PACKAGE_ environment variable
  to use your local pyprojectx copy in another project.
```shell
# Linux, Mac
export PYPROJECTX_PACKAGE=path/to/pyprojectx
# windows
set PYPROJECTX_PACKAGE=path/to/pyprojectx
```
