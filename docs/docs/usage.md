# Usage

## CLI
```
--8<-- "docs/usage.txt"
```

## Initialize a new or existing project
Pyprojectx can create or update a `pyproject.toml` file for either a plain, a [PDM](https://pdm.fming.dev/)
or a [Poetry](https://python-poetry.org/) project.

Cd into your existing project directory (or create a new empty directory), download the wrapper scripts,
and run the init command.

!!! tip "Tip: Add the wrapper scripts to version control"
    When using Git:
    ```shell
    git add pw pw.bat
    git update-index --chmod=+x pw
    echo .pyprojectx/ >> .gitignore
    ```

### Plain Python project
=== "Linux/Mac"
    ```bash
    curl -LO https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip && unzip wrappers.zip && rm -f wrappers.zip
    ./pw --init project
    ```

=== "Windows"
    ```powershell
    Invoke-WebRequest https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip -OutFile wrappers.zip; Expand-Archive -Path wrappers.zip -DestinationPath .; Remove-Item -Path wrappers.zip
    .\pw --init project
    ```

Now you can use the `pw` or [`px`](/usage/#install-the-global-px-script) script to show available tools and commands: `./pw -i`.

### PDM project
Start the interactive PDM initializer:
=== "Linux/Mac"
    ```bash
    curl -LO https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip && unzip wrappers.zip && rm -f wrappers.zip
    ./pw --init pdm
    ```

=== "Windows"
    ```powershell
    Invoke-WebRequest https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip -OutFile wrappers.zip; Expand-Archive -Path wrappers.zip -DestinationPath .; Remove-Item -Path wrappers.zip
    .\pw --init pdm
    ```

Any extra arguments are passed to PDM's init command, f.e. `./pw --init pdm --non-interactive`.

Now you can run any PDM command with the `pw` or [`px`](/usage/#install-the-global-px-script) script, f.e. `./pw pdm install`

### Poetry project
Start the interactive poetry initializer:
=== "Linux/Mac"
    ```bash
    curl -LO https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip && unzip wrappers.zip && rm -f wrappers.zip
    ./pw --init poetry
    ```

=== "Windows"
    ```powershell
    Invoke-WebRequest https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip -OutFile wrappers.zip; Expand-Archive -Path wrappers.zip -DestinationPath .; Remove-Item -Path wrappers.zip
    .\pw --init poetry
    ```

Any extra arguments are passed to Poetry's init command, f.e. `./pw --init poetry --no-interaction`.

Now you can run any Poetry command with the `pw` or [`px`](/usage/#install-the-global-px-script) script, f.e. `./pw poetry install`

!!! info "In-project virtual environment"
    `--init poetry` will also copy a `poetry.toml` to your project directory:
    ```toml
    [virtualenvs]
    in-project = true
    ```
    This makes Poetry create a `.venv` in your project directory instead of somewhere in your home directory.
    It makes it easier to locate files and to keep your system clean when removing the project.

## Install the global `px` script
Pyprojectx provides a small `px` script that delegates everything to the `pw` wrapper script.
The `pw` script is searched for in the current working directory and its parents.

When added to your _PATH_, you can replace `./pw` with the shorter `px`.
This also works from subdirectories: `../../pw` can also be replaced with `px`

To install:
=== "Linux/Mac"
    ```bash
    ./pw --init global
    ```

=== "Windows"
    ```powershell
    .\pw --init global
    ```

## Global tools
Besides the `px` script, `pw --init global` also copies other files:

* `pxg` script in `~/.pyprojectx`
* `pw` script and example `pyproject.toml` in `~/.pyprojectx/global`

`pxg` can be used as a lightweight [pipx](https://pypa.github.io/pipx/) to install tools globally.

Example usage: `pyproject.toml` contains by default [httpie](https://httpie.io/) so you can make http requests:
```shell
pxg http POST pie.dev/post hello=world
```

Uninstalling all global tools is just a matter of `rm -rf ~/.pyprojectx/global/.pyprojectx`
