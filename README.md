# pyprojectx
Execute scripts from pyproject.toml, installing tools on-the-fly

Getting started with a Python project should be a one-liner:
```shell
git clone https://github.com/houbie/pyprojectx.git && cd pyprojectx && ./pw build
```

Pyprojectx provides a CLI wrapper for automatic installation of Python tools:
* Make it be a breeze for others to get started with your project or tutorial
* Get reproducible builds by always using the correct versions of your build tools
* Plays well with build tools like [Poetry](https://python-poetry.org/)

Pyprojectx brings `npm run` to Python with:
* less keystrokes
* isolated dependencies: tools are not required to be development dependencies


## Installation
No tools to install (besides Python 3) 😍

![Cast](./docs/poetry-build-cast.svg)

Copy the *nix and widows commands, _pw_ and _pw.bat_, to your project's root directory and add them under version control.

_python3_ (or _python_ on Windows) >= 3.6 and _pip3_ must be available on your path.

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

The _tool.pyprojectx.alias_ section can contain optional commandline aliases in the form

`alias = [tool_key:] command`


Example:
```toml
[tool.pyprojectx.alias]
# convenience shortcuts
run = "poetry run"
test = "poetry run pytest"
pylint = "poetry run pylint"

# tell pw that the bandit binary is installed as part of flake8
bandit = "flake8: bandit my_package tests -r"

# simple shell commands (watch out for variable substitutions and string literals containing whitespace or special characters )
clean = "rm -f .coverage && rm -rf .pytest_cache"

# when combining multiple pyprojectx aliases, prefix them with ./pw
# this works on *nix and windows and in sub folders because ./pw will be replaced with the correct script path
check = "./pw pylint && ./pw test"
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
Add `path\to\pw` in front of the usual command line.

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

_pw_ specific options:
```shell
# clear and re-install the virtual environment for a tool
./px --force-install poetry
```

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
To clean up everything that was installed via pyprojectx, just delete the _.pyprojectx_ directory in your home directory.

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
* [Pyprojectx examples](https://github.com/houbie/wrapped-pi)
* [Facebook's PathPicker fork](https://github.com/houbie/PathPicker) (using Poetry)

## TODO
* move most logic to a library that can be published to PyPi
* px script for Windows
* init script that copies the pw scripts and initializes pyproject.toml
