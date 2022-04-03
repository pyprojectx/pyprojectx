# Recipes

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
```toml
[tool.pyprojectx]
# the first time that a poetry command is invoked, we make sure that pre-commit hooks are installed, so we can't forget it
poetry = { requirements = "poetry==1.1.13", post-install = "pw@pre-commit install" }
black = "black==22.1.0"
isort = "isort==5.10.1"
pylint = "pylint==2.12.2"
pre-commit = "pre-commit"
mkdocs = ["mkdocs ~=1.2", "mkdocs-material ~=8.2", "mkdocstrings[python] ~=0.18", "markdown-include ~=0.6", ]

[tool.pyprojectx.aliases]
install = "poetry install"
run = "poetry run pyprojectx -t pyproject.toml "
outdated = "poetry show --outdated"
clean = "rm -r .venv .pytest_cache dist"
black = "black src tests"
isort = "isort src tests"
unit-test = "poetry run pytest tests/unit"
integration-test = "poetry run pytest tests/integration"
test = "pw@unit-test && pw@integration-test"
check-pylint = "pylint src tests"
check-black = "black src tests --check"
# run check before pushing to git and your build will never break
check = "pw@check-black && pw@check-pylint && pw@test"
# run the same build command on your laptop or CI/CD server
build = "pw@install && pw@check && pw@poetry build"

# extract complexity from your CI/CD flows to test/run locally
publish = "poetry publish --username __token__"
prep-release = """\
# create distributions, tag versions, etc.
"""

# generate documentation
generate-usage = "pw@ --help > docs/docs/usage.txt"
serve-docs = "@mkdocs: cd docs && mkdocs serve"
deploy-docs = "@mkdocs: cd docs && mkdocs gh-deploy"
```

See Pyprojectx own [pyproject.toml](https://github.com/pyprojectx/pyprojectx/blob/main/pyproject.toml) for a full example
with Poetry, or [px-demo](https://github.com/pyprojectx/px-demo) for an example project with PDM.


## Github actions
By using the `pw` wrapper script, you can simplify your github actions:
* no explicitly tool installations or docker images (for Python tools)
* use the same commands and scripts in github actions as on your laptop

Some tips:
* Use the same scripts on Linux and Windows by replacing `./pw` (resp. `.\pw`) with `python pw`
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
# install the current directory together with jupyter
jupyter = ["jupyter", "."]

[tool.pyprojectx.aliases]
# the notebook-dir is optional
# -y is there to automatically answer 'yes' after quiting with ctrl+c
notebook = "jupyter notebook --notebook-dir docs -y"
```
Just run `px notebook` or even `px n`
