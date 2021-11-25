# pyprojectx
Execute scripts from pyproject.toml, installing tools on-the-fly

Getting started with a Python project should be a one-liner:
```shell
git clone https://github.com/houbie/pyprojectx.git && cd pyprojectx && ./pw build
```

![Cast](./docs/poetry-build-cast.svg)

Pyprojectx provides a CLI wrapper for automatic installation of Python tools:
* Make it be a breeze for others to get started with your project or tutorial
* Get reproducible builds by always using the correct versions of your build tools
* Plays well with build tools like [Poetry](https://python-poetry.org/)

Pyprojectx brings `npm run` to Python with:
* less keystrokes
* isolated dependencies: tools are not required to be development dependencies

## Installation
Copy the *nix and widows commands, _pw_ and _pw.bat_, to your project's root directory and add them under version control.

### osx / linux
```shell
curl -s https://raw.githubusercontent.com/houbie/pyprojectx/0.9.0/src/pyprojectx/wrapper/pw.py -o pw && curl -s https://raw.githubusercontent.com/houbie/pyprojectx/0.9.0/src/pyprojectx/wrapper/pw.bat -o pw.bat && chmod a+x pw
```

### windows
```shell
curl -s https://raw.githubusercontent.com/houbie/pyprojectx/0.9.0/src/pyprojectx/wrapper/pw.py -o pw && curl -s https://raw.githubusercontent.com/houbie/pyprojectx/0.9.0/src/pyprojectx/wrapper/pw.bat -o pw.bat
```
**NOTE** On windows you need to explicitly mark the osx/linux script as executable before adding it to version control.
When using git:
```shell
git add pw pw.bat
git update-index --chmod=+x pw
```

## Configuration
Add the _tool.pyprojectx_ section inside _pyproject.toml_ in your project's root directory.

Each entry has the form

`tool = "pip-install-arguments"`

Example:
```toml
[tool.pyprojectx]
# require a specific poetry version
poetry = "poetry==1.1.11"
# use the latest black
black = "black"
# install flake8 in combination with plugins
flake8 = """
flake8
flake8-bandit
pep8-naming
flake8-isort
flake8-pytest-style"""
```

The _tool.pyprojectx.aliases_ section can contain optional commandline aliases in the form

`alias = [@tool_key:] command`


Example:
```toml
[tool.pyprojectx.alias]
# convenience shortcuts
run = "poetry run"
test = "poetry run pytest"
pylint = "poetry run pylint"

# tell pw that the bandit binary is installed as part of flake8
bandit = "@flake8: bandit my_package tests -r"

# simple shell commands (watch out for variable substitutions and string literals containing whitespace or special characters )
clean = "rm -f .coverage && rm -rf .pytest_cache"

# when running an alias from within another alias, prefix it with `pw@`
check = "pw@pylint && pw@test"
```

Aliases can be invoked as is or with extra arguments:
```shell
./pw bandit

./pw poetry run my-script
# same as above, but using the run alias
./pw run my-script
```

## Isolation
Each tool gets installed in an isolated virtual environment.

These are all located in the user's platform-specific home directory under _.pyprojectx/venvs_.

This location can be modified by setting the `PYPROJECTX_HOME` environment variable (f.e. on your CI/CD server).

# Usage
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

Check _pw_ specific options with `pw --help`

## Bonus
If you want to avoid typing `./pw` (or `../pw` when in a subdirectory), you can copy the _rp_ (_run pyprojectx_) script to a
location on your PATH (f.e. _/usr/local/bin_, or create a symlink with `ln -fs $(pwd)/px /usr/local/bin/px`).

From then on, you can replace _pw_ with _rp_ and invoke it from any (sub)directory containing the _pw_ script.
```shell
cd my-pyprojectx-project
px test
cd tests
px test sometest.py
```

## Uninstall / cleaning up
Delete the _.pyprojectx_ directory in your project's root.

## Why yet another tool when we already have pipx etc.?
* As Python noob I had hard times setting up a project and building existing projects
* There is always someone in the team having issues with his setup, either with a specific tool, with Homebrew, pipx, ...
* Adding tools as dev dependencies often leads to dependency conflicts
* Different projects often require different versions of the same tool

## Best practices
* Separate your tools from your project dependencies
* Use a build tool with decent dependency management that locks all dependencies,
  f.e. [Poetry](https://python-poetry.org/) or [PDM](https://pdm.fming.dev/)
* Pin down the version of your build tool to prevent the "project doesn't build anymore" syndrome.
  Eventually a new version of the build tool with breaking changes will be released.
* There is a category of tools that you don't want to version: tools that interact with changing environments.
  You probably want to update those on a regular basis by running `./pw --upgrade my-evolving-tool`.

## Examples
* This project (using Poetry)
* Projects that still use the **python-wraptor** scripts and need to be migrated to **pyprojectx**
  * [Pyprojectx examples](https://github.com/houbie/wrapped-pi)
  * [Facebook's PathPicker fork](https://github.com/houbie/PathPicker) (using Poetry)

## TODO
* px script for Windows
* init script that copies the pw scripts and initializes pyproject.toml

## Development
* Build/test:
```shell
git clone git@github.com:houbie/pyprojectx.git
cd pyprojectx
./pw build
```

* Set the path to pyprojectx in the _PYPROJECTX_PACKAGE_ environment variable
 to use your local pyprojectx copy in another project.
```shell
# *nix
export PYPROJECTX_PACKAGE=path/to/pyprojectx
# windows
set PYPROJECTX_PACKAGE=path/to/pyprojectx
```
