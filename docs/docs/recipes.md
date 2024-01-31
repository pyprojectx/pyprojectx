# Recipes

## Create a new project
Install common tools:
- pdm or poetry: dependency management (see [simple projects](#simple-projects) if not required).
- ruff: linter/formatter
- pre-commit: git hooks for formatting and linting
- px-utils: cross-platform file operations

=== "Linux/Mac"
```bash
# initialize a PDM project
./pw --add pdm,ruff,pre-commit,px-utils
./pw pdm init
# initialize a poetry project
./pw --add poetry,ruff,pre-commit,px-utils
./pw poetry init
```

=== "Windows"
```powershell
# initialize a PDM project
pw --add pdm,ruff,pre-commit,px-utils
pw pdm init
# initialize a poetry project
pw --add poetry,ruff,pre-commit,px-utils
pw poetry init
```

## Simple projects
If you don't need dependency management (f.e. when you don't have any dependencies),
Pyprojectx can create your virtual environment and install test dependencies.

```toml
[tool.pyprojectx]
[tool.pyprojectx.main]
requirements = ["pre-commit", "black", "isort", "mypy", "px-utils"]
post-install = "pre-commit install && pw@ --install-context venv"

[tool.pyprojectx.venv]
dir = "@PROJECT_DIR/.venv"
# install your project in editable mode; this assumes that your project is installable
requirements = ["pytest==8.0.0", "-e ."]

[tool.pyprojectx.aliases]
format = ["black src", "isort src"]
lint = "mypy --python-executable .venv/bin/python --no-incremental"
test = { cmd = "pytest", ctx = "venv" }
```

After running any alias (f.e. `./pw test`), you can activate the virtual environment with `source .venv/bin/activate`.

Use the `-f` of `--force-install` flag to recreate the virtual environment
after changing the requirements in `[tool.pyprojectx.venv]`, f.e. run `./pw -f test`.


## Build scripts
Script your development and build flow with aliases:

* use pre-commit hooks
* configure code formatting and linting
* package and publish to pypi
* ...

Use [Poetry](https://python-poetry.org/) or [PDM](https://pdm.fming.dev/) to further streamline your development flow with:

* better dependency management and version locking compared with pip requirement files
* virtual environment management (or skip a virtual environment all together when using PDM)
* packaging and publishing

With this combination, you can most likely skip makefiles altogether.

Example:

=== "PDM"
    ```toml
    [tool.pyprojectx]
    [tool.pyprojectx.main]
    requirements = [ "pdm", "ruff", "pre-commit", "px-utils", "mkdocs" ]
    # the first time that a pdm command is invoked, we make sure that pre-commit hooks are installed, so we can't forget it
    post-install = "pre-commit install"
    [tool.pyprojectx.aliases]
    # create the virtual environment and install all dependencies
    install = "pdm install"
    # run a command in the project's virtual environment
    run = "pdm run"
    # show outdated dependencies
    outdated = "pdm update --outdated"
    clean = "pxrm .venv .pytest_cache dist .pdm-build .ruff_cache"
    full-clean = ["@clean", "pxrm .pyprojectx"]
    # format code and sort imports
    format = ["ruff format", "ruff check --select I --fix"]
    lint = ["ruff check"]
    test = "pdm run pytest"
    # run check before pushing to git and your build will never break
    check = ["@lint", "@test"]
    # run the same build command on your laptop or CI/CD server
    build = [ "@install", "@check", "pdm build" ]
    # extract complexity from your CI/CD flows to test/run them locally
    # use comprehensible python scripts (bin/prep-release) instead of complex shell scripts
    release = ["prep-release", "pdm publish --username __token__"]
    ```

=== "Poetry"
    ```toml
    [tool.pyprojectx]
    [tool.pyprojectx.main]
    requirements = [ "poetry", "ruff", "pre-commit", "px-utils", "mkdocs" ]
    # the first time that a poetry command is invoked, we make sure that pre-commit hooks are installed, so we can't forget it
    post-install = "pre-commit install"
    [tool.pyprojectx.aliases]
    # create the virtual environment and install all dependencies
    install = "poetry install"
    # run a command in the project's virtual environment
    run = "poetry run"
    # show outdated dependencies
    outdated = "poetry show --outdated --top-level"
    clean = "pxrm .venv .pytest_cache dist .ruff_cache"
    full-clean = ["@clean", "pxrm .pyprojectx"]
    # format code and sort imports
    format = ["ruff format", "ruff check --select I --fix"]
    lint = ["ruff check"]
    test = "poetry run pytest"
    # run check before pushing to git and your build will never break
    check = ["@lint", "@test"]
    # run the same build command on your laptop or CI/CD server
    build = [ "@install", "@check", "poetry build" ]
    # extract complexity from your CI/CD flows to test/run them locally
    # use comprehensible python scripts (bin/prep-release) instead of complex shell scripts
    release = ["prep-release", "poetry publish --username __token__"]
    ```

See Pyprojectx own [pyproject.toml](https://github.com/pyprojectx/pyprojectx/blob/main/pyproject.toml) for a full example
with PDM, or [px-demo](https://github.com/pyprojectx/px-demo) for another example project with PDM or
the poetry [variant](https://github.com/pyprojectx/px-demo/tree/poetry).

!!! tip "Tip: Keep the poetry virtual environment inside your project directory"
    Add `poetry.toml` to your project:
    ```toml
    [virtualenvs]
    in-project = true
    ```
    This makes Poetry create a `.venv` in your project directory instead of somewhere in your home directory.
    It makes it easier to locate files and to keep your system clean when removing the project.

## Github actions
By using the `pw` wrapper script, you can simplify your github actions:

* no explicitly tool installations or docker images (for Python tools)
* use the same commands and scripts in github actions as on your laptop

Some tips:

* Use the same scripts on Linux and Windows by replacing `./pw` (resp. `pw`) with `python pw`
* Speed up builds by caching `.pyprojectx`

Example:
```yaml
jobs:
  build:
    steps:
      - name: Cache .pyprojectx
        uses: actions/cache@v2
        env:
          cache-name: .pyprojectx
        with:
          path: .pyprojectx
          key: ${{ runner.os }}-pyprojectx

      - name: Set up Python ${{ matrix.python-version }} on ${{ matrix.os }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}

      - name: Test and build
        run: python pw build
```
See Pyprojectx own [build](https://github.com/pyprojectx/pyprojectx/blob/main/.github/workflows/build.yml)
and [release](https://github.com/pyprojectx/pyprojectx/blob/main/.github/workflows/release.yml) workflows for a full example.

## Experiment with your project in a Jupyter notebook
You can launch a notebook that has access to your project packages without the need to install anything upfront.

```toml
[tool.pyprojectx]
# install the current project in editable mode, together with jupyter
jupyter = ["jupyterlab", "-e ."]

[tool.pyprojectx.aliases]
# -y is there to automatically answer 'yes' after quitting with ctrl+c
notebook = "jupyter lab -y"
```
Just run `px notebook` or even `px n`

!!! note "Editable installs are not locked"

    When a tool context contains an editable install, it won't be locked when running `./pw --lock`.
    Therefore, it is recommended to add editable install to a separate tool context and lock the main
    context fro reproducible builds.
