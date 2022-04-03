# Manage Tools as Dev dependencies

Pyprojectx can manage all the Python tools and utilities that you use for building, testing...

Adding a tool to the `[tool.pyprojectx]` section in `pyproject.toml` makes it available inside your project.

!!! info "`px` or `pw`?"
    This section assumes that you installed the [px utility script](/usage/#install-the-global-px-script).
    Otherwise, you need to replace `px` with `./pw` (Linux, Mac) or `.\pw` (Windows PowerShell).

## Tool configuration

Pyprojectx creates an isolated virtual environment for each configured tool (or set of tools).

Inside the `[tool.pyprojectx]` section of `pyproject.toml` you specify what needs to be installed.

```toml title="pyproject.toml"
[tool.pyprojectx]
# require a specific poetry version
poetry = "poetry==1.1.11"
# install the latest version of the black formatter
black = "black"
```

Above configuration makes the `black` and `poetry` commands available inside your project.

You only need to prefix them with the`px` or `pw` wrapper script:

=== "Any OS with `px`"

    ```bash
    px poetry --help
    px black my_package --diff
    ```

=== "Linux/Mac"

    ```bash
    ./pw poetry --help
    ./pw black my_package --diff
    ```

=== "Windows"

    ```powershell
    .\pw poetry --help
    .\pw black my_package --diff
    ```

## Specifying requirements

The entries in the `[tool.pyprojectx]` section take the form `tool = requirements`

* _tool_: The main command or script that comes with the tool. If the tool comes with additional commands that you want
  to use, you need to expose these via Pyprojectx [aliases](/config/aliases).
* _requirements_: A multiline string or array of strings that adheres to
  pip's [Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/#requirements-file-format)

Example:

```toml title="pyproject.toml"
[tool.pyprojectx]
# expose httpie's http script
http = "httpie ~= 3.0"

flake8 = """
  flake8 >3
  flake8-bugbear >=20
"""

black8 = ["flake8 ~=4.0", "flake8-black ~=0.3"]

[tool.pyprojectx.aliases]
run-flake8-with-black = "@black8: flake8"
```

With above configuration, you can run following commands:

```bash
px http www.google.com
# HTTP/1.1 200 OK ...

px flake8 --version
# 4.0.1 (flake8-bugbear: 22.1.11, mccabe: 0.6.1, pycodestyle: 2.8.0, pyflakes: 2.4.0) CPython 3.9.6 on Darwin

px run-flake8-with-black --version
# 4.0.1 (black: 0.3.2, mccabe: 0.6.1, pycodestyle: 2.8.0, pyflakes: 2.4.0) CPython 3.9.6 on Darwin
```

!!! tip "Tip: Specify exact versions for tools that are critical in your build flow"

    This makes sure that your build won't break when new versions of a tool are released.
    It also ensures that you can always rebuild older versions of your project that rely on older versions of tools
    (f.e. when building a patch release).

## Using an alternative package index

You can use pip's `--index-url` or `--extra-index-url` to install packages from alternative (private) package indexes:

```toml
[tool.pyprojectx]
my-private-tool = [
    "--extra-index-url https://artifactory.acme.com/artifactory/api/pypi/python-virtual/simple",
    "some-private-package"
]
```

## Post-install scripts
In some situations it can be useful to perform additional actions after a tool has been installed.
This is achieved by configuring both requirements and post-install scripts for a tool:
```toml
[tool.pyprojectx]
[tool.pyprojectx.jupyter]
requirements = ["jupyter",	"jupyter_contrib_nbextensions"]
post-install="""\
jupyter contrib nbextension install --sys-prefix
jupyter nbextension enable autoscroll/main --sys-prefix
jupyter nbextension enable scroll_down/main --sys-prefix"""
```

When running `px jupyter notebook` for the first time in the example above,
some Jupyter extensions are installed and enabled.

!!! tip "Tip: Use toml subsections for better readability"

    The example above uses a toml subsection instead of an inline table:
    ```toml
    jupyter = { requirements = [...], post-install="..."}`
    ```
