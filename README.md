# pyprojectx

Execute scripts from pyproject.toml, installing tools on-the-fly

Getting started with a Python project should be a one-liner:
```shell
git clone https://github.com/houbie/pyprojectx.git && cd pyprojectx && ./pw build
```

![Cast](https://raw.githubusercontent.com/houbie/pyprojectx/main/docs/poetry-build-cast.svg)

Pyprojectx provides a CLI wrapper for automatic installation of Python tools:
* Make it be a breeze for others to get started with your project or tutorial
* Get reproducible builds by always using the correct versions of your build tools
* Plays well with build tools like [Poetry](https://python-poetry.org/) and [PDM](https://pdm.fming.dev/)

Pyprojectx brings `npm run` to Python with:
* less keystrokes
* isolated dependencies: tools are not required to be development dependencies

## Installation
Copy the [wrapper scripts](https://github.com/houbie/pyprojectx/releases/latest/download/wrappers.zip)
into the root of your project.

Python >= 3.7 must be available on your PATH.

* osx / linux :
```shell
curl -LO https://github.com/houbie/pyprojectx/releases/latest/download/wrappers.zip && unzip wrappers.zip && rm -f wrappers.zip
```

* windows: unpack the [wrappers zip](https://github.com/houbie/pyprojectx/releases/latest/download/wrappers.zip)

**NOTE** On windows you need to explicitly mark the osx/linux script as executable before adding it to version control.
When using git:
```shell
git add pw pw.bat
git update-index --chmod=+x pw
```

## Configuration
Add the _tool.pyprojectx_ section inside _pyproject.toml_ in your project's root directory.

Each entry has the form `tool = "pip-requirements"`, where _pip-requirements_ adheres to the
[requirements file format](https://pip.pypa.io/en/stable/reference/requirements-file-format/).

Example:
```toml
[tool.pyprojectx]
# require a specific poetry version
poetry = "poetry==1.1.11"
# use the latest black
black = "black"
# install flake8 in combination with plugins; one line per requirement 
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

These are all located in the _.pyprojectx_ directory of your project
(where _pyproject.toml_ is located).

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

When you run an alias on the command-line, you don’t have to provide the full name of the alias.
You only need to provide enough of the alias name to uniquely identify it.
For example, it’s likely `./pw che` is enough to run the _check_ alias if it exists.

You can use camel case patterns for more complex abbreviations. These patterns are expanded to match camel case
and kebab case names. For example the pattern foBa (or even fB) matches fooBar and foo-bar.

**NOTE** aliases can hide tool commands. F.e. a _pylint-src_ alias will hide the _pylint_ tool and will always run
when running `./pw pylint some args`. This can be solved by making sure that no alias name starts with _pylint_ or by
adding _pylint_ as an alias: `pylint="pylint"`.

Check _pw_ specific options with `pw --help`

## Project initialization
Initialize a new or existing project with the _--init_ option.
* `./pw --init project`: add pyprojectx example sections to an existing or new _pyproject.toml_ in the current directory.
* `./pw --init poetry`: initialize a [Poetry](https://python-poetry.org/) project and add pyprojectx example sections to _pyproject.toml_.
* `./pw --init pdm`: initialize a [PDM](https://pdm.fming.dev/) project and add pyprojectx example sections to _pyproject.toml_.
* `./pw --init global`: initialize a global pyprojectx setup in your home directory that can be accessed with the _pgx_ command.
This turns pyprojectx into a lightweight [Pipex](https://pypa.github.io/pipx/) alternative.
* `./pw --init` or `./pw --init help`:  show initializer help.

## px: run pw from any subdirectory
If you want to avoid typing `./pw` (or `../pw` when in a subdirectory), you can install the _px_
script in your home directory with `./pw --init global` (or `pw --init global` on Windows) and
add _~/.pyprojectx_ to your PATH.

From then on, you can replace _pw_ with _px_ and invoke it from any (sub)directory containing the _pw_ script.
```shell
cd my-pyprojectx-project
px test
cd tests
px test sometest.py
```

## Uninstall / cleaning up
* Delete the _.pyprojectx_ directory in your project's root.
* Delete the global _.pyprojectx_ directory in your home directory.

## Why yet another tool when we already have pipx etc.?
* As Python noob I had hard times setting up a project and building existing projects
* There is always someone in the team having issues with his setup, either with a specific tool, with Homebrew, pipx, ...
* Adding tools as dev dependencies impacts your production dependencies and can even lead to unresolvable conflicts
* Different projects often require different versions of the same tool

## Best practices
* Separate your tools from your project dependencies
* Use a build tool with decent dependency management that locks all dependencies,
  f.e. [Poetry](https://python-poetry.org/) or [PDM](https://pdm.fming.dev/)
* Pin down the version of your build tool to prevent the "project doesn't build anymore" syndrome.
  Eventually a new version of the build tool with breaking changes will be released.
* There is a category of tools that you don't want to version: tools that interact with changing environments.

## Examples
* This project (using Poetry)
* [px-demo](https://github.com/houbie/px-demo)

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
