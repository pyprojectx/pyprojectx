# Manage tools as dev dependencies

Pyprojectx can manage all the Python tools and utilities that you use for building, testing...

Adding tools to the `[tool.pyprojectx]` section in `pyproject.toml` makes them available inside your project.

!!! note "Tool contexts introduced in Pyprojectx 2.0.0"

    Prior to Pyprojectx 2.0.0, tools were always installed in a separate virtual environment.
    As of 2.0.0, tools are by default installed in the virtual environment of the _main_ tool context.

!!! info "`px` or `pw`?"
    This section assumes that you installed the [px utility script](/usage/#install-the-global-px-script).
    Otherwise, you need to replace `px` with `./pw` (Linux, Mac) or `pw` (Windows PowerShell).

## Tool contexts

Pyprojectx creates an isolated virtual environment for each tool context (set of tools).

Inside the `[tool.pyprojectx]` section of `pyproject.toml` you specify what needs to be installed.

```toml title="pyproject.toml"
[tool.pyprojectx]
# require a specific poetry version, use the latest version of black
main = ["poetry==1.1.11", "black"]
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
    pw poetry --help
    pw black my_package --diff
    ```

!!! note "Naming your tool context"

    When running a command that has the same name as a tool context, the command will be executed by default inside the virtual environment of that tool context.
    Otherwise, the command will be executed in the virtual environment of the _main_ tool context.


## Tool context activation

If you don't want to prefix every command with `px` or `./pw`, you can activate a tool context.

For example, to activate the `main` tool context run `source .pyprojectx/main/activate`.
This makes all the tools in the _main_ context available in your shell.

Alternatively, you can add _.pyprojectx/main_ to your _PATH_.

!!! note "Upgrading from Pyprojectx < 2.1.0"

    If the virtual environment of a tool cotext is already present, you will need to re-create it
    to use the new activation mechanism, either by removing the _.pyprojectx_ directory or by running
    any command with the `--force-install` option, f.e. `./pw -f --install-context main`.



## Tool context configuration

In its simplest form, a tool context is a multiline string or array of strings that adheres to pip's [Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/#requirements-file-format)

Example:

```toml title="pyproject.toml"
[tool.pyprojectx]
main = ["pdm","ruff","pre-commit","px-utils"]
http = "httpie ~= 3.0"
```

With above configuration, you can run following commands:

```bash
px pdm --version
# PDM, version 2.11.2
px http www.google.com
# HTTP/1.1 200 OK ...
```

!!! tip "Tip: [Lock](#locking-requirements) your tool requirements"

    This makes sure that your build won't break when new versions of a tool are released,or when a
    <a href="https://upcycled-code.com/blog/the-broken-version-breakdown">tool is broken by a new release of one of its dependencies</a>.

You can also include requirements from a text file or _pyproject.toml_ file with `-r`:

```toml
[tool.pyprojectx]
main = ["-r pyproject.toml", "-r dev-requirements.txt"]
```

If you want to install a prerelease version of a tool, you need to configure it:
```toml
[tool.pyprojectx]
prerelease = "allow"
```

## Post-install scripts
In some situations it can be useful to perform additional actions after a tool has been installed.
This is achieved by configuring both requirements and post-install scripts for a tool

```toml
[tool.pyprojectx]
[tool.pyprojectx.main]
requirements = ["pdm", "ruff", "pre-commit", "px-utils"]
post-install = "pre-commit install"
```

When creating your project's virtual environment with `px pdm install` for the first time in the example above,
pre-commit is also initialised. This makes sure that pre-commit hooks are always run when committing code.

!!! tip "Tip: Use toml subsections for better readability"

    The example above uses a toml subsection instead of an inline table:
    ```toml
    main = { requirements = [...], post-install="..."}`
    ```

## Using an alternative package index

You can use pip's `--index-url` or `--extra-index-url` to install packages from alternative (private) package indexes:

```toml
[tool.pyprojectx]
private-tool = [
    "--extra-index-url https://artifactory.acme.com/artifactory/api/pypi/python-virtual/simple",
    "some-private-package"
]
```

## Locking requirements
To achieve reproducible builds, you can lock the versions of all tools that you use in your project by:

* creating a _pw.lock_ file
* pinning tool versions in _pyproject.toml_

### Creating a _pw.lock_ file
When you run `./pw --lock`, a _pw.lock_ file is created in the root directory of your project.
This file should be committed to version control.

This is the recommended way to lock tool versions to guarantee reproducible builds (see [why](/dev-dependencies#the-unreliable-pip-install))

The lock file is automatically updated when the tool context requirements in _pyproject.toml_ change.

To upgrade all tools to the latest version (respecting the requirements in _pyproject.toml_),
combine the _lock_ option with the _force-install_ option: `./pw --lock -f`.

!!! note "Supporting multiple Python versions"

    When generating the lock file, the version of the current Python interpreter is used as minimum
    version that should be supported by the resolved requirements.
    You can override this by configuring the _lock-python-version_, e.g., `3.9` or `3.9.23`:
    ```toml
    [tool.pyprojectx]
    lock-python-version = "3.9"
    ```

!!! tip "Tip: don't specify tool versions in _pyproject.toml_ when using a _pw.lock_ file"

    When there is no version specified for a tool, the latest version will be installed and locked.
    Updating all tools to the latest version is then as simple as running `./pw --lock` again.
    In case of conflicts or issues with a new version, you can always revert to the previous version of the lock file.

### Pinning tool versions in _pyproject.toml_
You can also pin tool versions in _pyproject.toml_:

```toml
[tool.pyprojectx]
main = ["pdm==2.11.2", "ruff==0.1.11", "pre-commit==3.6.0", "px-utils==1.0.1"]
```
Be aware that even with a fixed version, [tools can break at future installs](/dev-dependencies#the-unreliable-pip-install)!
