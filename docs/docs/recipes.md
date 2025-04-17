# Recipes

## Create a new project
Install common tools:
- uv, pdm or poetry: dependency management
- ruff: linter/formatter
- pre-commit: git hooks for formatting and linting
- px-utils: cross-platform file operations

### uv based projects
`uv` only allows to initialize a project when there is no `pyproject.toml` present in the project dir.
Fortunately, uv is available by default in the main tool context, so we can use it to initialize the project.

=== "Linux/Mac"
    ```bash
    # download the wrapper scripts
    curl -LO https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip && unzip -o wrappers.zip && rm -f wrappers.zip
    # initialize a uv project in a (empty) directory without pyproject.toml
    ./pw uv init
    # add common tools to the project, including uv
    ./pw --add uv,ruff,pre-commit,px-utils
    # have uv create the virtual environment and install the dependencies
    ./pw uv sync
    # call the main script to show that the project is set up correctly
    ./pw uv run main.py
    # lock the tool versions for reproducible builds
    ./pw --lock
    ```

=== "Windows"
    ```powershell
    # download the wrapper scripts
    Invoke-WebRequest https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip -OutFile wrappers.zip; Expand-Archive -Force -Path wrappers.zip -DestinationPath .; Remove-Item -Path wrappers.zip
    # initialize a uv project in a (empty) directory without pyproject.toml
    pw uv init
    # add common tools to the project, including uv
    pw --add uv,ruff,pre-commit,px-utils
    # have uv create the virtual environment and install the dependencies
    pw uv sync
    # call the main script to show that the project is set up correctly
    pw uv run main.py
    # lock the tool versions for reproducible builds
    pw --lock
    ```

You can run `./pw uv init --help` to see the available options or consult the [uv documentation](https://docs.astral.sh/uv/reference/cli/#uv-init).
See also [px-demo](https://github.com/pyprojectx/px-demo) for a full example.

### PDM or Poetry based projects

=== "Linux/Mac"
    ```bash
    # download the wrapper scripts
    curl -LO https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip && unzip -o wrappers.zip && rm -f wrappers.zip
    # initialize a PDM project
    ./pw --add pdm,ruff,pre-commit,px-utils
    ./pw pdm init
    # initialize a poetry project
    ./pw --add poetry,ruff,pre-commit,px-utils
    ./pw poetry init
    # lock the tool versions for reproducible builds
    ./pw --lock
    ```

=== "Windows"
    ```powershell
    # download the wrapper scripts
    Invoke-WebRequest https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip -OutFile wrappers.zip; Expand-Archive -Force -Path wrappers.zip -DestinationPath .; Remove-Item -Path wrappers.zip
    # initialize a PDM project
    pw --add pdm,ruff,pre-commit,px-utils
    pw pdm init
    # initialize a poetry project
    pw --add poetry,ruff,pre-commit,px-utils
    pw poetry init
    # lock the tool versions for reproducible builds
    ./pw --lock
    ```

## Simple projects
If you don't need dependency management (f.e. when you don't have any dependencies),
Pyprojectx can create your virtual environment and install test dependencies.

```toml
[tool.pyprojectx.venv]
# venv and .venv don't have any special meaning, you can choose any name
requirements = [
    "-r pyproject.toml", # optional: install project.dependencies from pyproject.toml
    "pytest" # test dependencies (keep your other dev dependencies in the main requirements)
]
dir = ".venv"

[tool.pyprojectx.main]
requirements = ["ruff", "pre-commit", "px-utils", "httpie", "build"]
post-install = "pre-commit install"

install = "pw@ --install-context venv"
test = { cmd = "pytest", ctx = "venv" }
format = ["ruff format", "ruff check --select I --fix"]
lint = ["ruff check"]
check = ["@lint", "@test"]
build = ["@install", "@check", "python -m build"]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
```

After running any alias (f.e. `./pw test`), you can activate the virtual environment with `source .venv/bin/activate`.
See also [px-demo](https://github.com/pyprojectx/px-demo/tree/simple) for a full example.

## Build scripts
Script your development and build flow with aliases:

* use pre-commit hooks
* configure code formatting and linting
* package and publish to pypi
* ...

Use [uv](https://docs.astral.sh/uv/) (or alternatively [Poetry](https://python-poetry.org/) or [PDM](https://pdm.fming.dev/)) to further streamline your development flow with:

* better dependency management and version locking compared with pip requirement files
* virtual environment management
* packaging and publishing

With this combination, you can most likely skip makefiles altogether.

Example:

=== "uv"
    ```toml
    [tool.pyprojectx]
    [tool.pyprojectx.main]
    requirements = [ "uv", "ruff", "pre-commit", "px-utils", "mkdocs" ]
    # the first time that a uv command is invoked, we make sure that pre-commit hooks are installed, so we can't forget it
    post-install = "pre-commit install"
    [tool.pyprojectx.aliases]
    # create the virtual environment and install all dependencies
    install = "uv sync"
    # run a command in the project's virtual environment
    run = "uv run"
    # show outdated dependencies
    outdated = "uv pip list --outdated"
    clean = "pxrm .venv .pytest_cache dist .ruff_cache"
    full-clean = ["@clean", "pxrm .pyprojectx"]
    # format code and sort imports
    format = ["ruff format", "ruff check --select I --fix"]
    lint = ["ruff check"]
    test = "@run pytest"
    # run check before pushing to git and your build will never break
    check = ["@lint", "@test"]
    # run the same build command on your laptop or CI/CD server
    build = [ "@install", "@check", "uv build" ]
    # extract complexity from your CI/CD flows to test/run them locally
    # use comprehensible python scripts (bin/prep-release) instead of complex shell scripts
    release = ["prep-release", "uv publish --username __token__"]
    ```

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

## GitHub actions
By using the `pw` wrapper script, you can simplify your GitHub actions:

* no explicitly tool installations or docker images (for Python tools)
* use the same commands and scripts in GitHub actions as on your laptop

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

## Run scripts that use the project's packages
You can set up a tool context that uses the project's virtual environment to run scripts.
Then you can make that context the default one for running scripts.

```toml
[tool.pyprojectx]
scripts_ctx = "venv"
[tool.pyprojectx.venv]
dir = ".venv" # not (directly) managed by pyprojectx
post-install = "@install" # optional: make sure the venv is ready to use
[tool.pyprojectx.aliases]
install = "uv sync" # optional: initialize the project's virtual environment using your preferred tool
```
Having a script `my-script.py` in the scripts directory, you can just run `px my-script` or even `px mS`.

## Experiment with your project in a Jupyter notebook
You can launch a notebook that has access to your project packages without the need to install anything upfront.

```toml
[tool.pyprojectx]
# install the current project in editable mode, together with jupyter; this requires that your project is installable
jupyter = ["jupyterlab", "-e ."]

[tool.pyprojectx.aliases]
# -y is there to automatically answer 'yes' after quitting with ctrl+c
notebook = "jupyter lab -y"
```
Just run `px notebook` or even `px n`

!!! note "Editable installs are not locked"

    When a tool context contains an editable install, it won't be locked when running `./pw --lock`.
    Therefore, it is recommended to add editable install to a separate tool context and lock the main
    context for reproducible builds.
