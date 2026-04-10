# Getting Started

!!! info "`px` or `pw`?"
    This guide uses `./pw` (Linux/Mac) and `pw` (Windows). Once you've installed the
    [px utility script](/usage#install-the-global-px-script), you can use the shorter `px` everywhere.

## Download the wrapper scripts

`cd` into your project directory and download the
[wrapper scripts](https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip):

=== "Linux/Mac"
    ```bash
    curl -LO https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip && unzip -o wrappers.zip && rm -f wrappers.zip
    ```

=== "Windows"
    ```powershell
    Invoke-WebRequest https://github.com/pyprojectx/pyprojectx/releases/latest/download/wrappers.zip -OutFile wrappers.zip; Expand-Archive -Force -Path wrappers.zip -DestinationPath .; Remove-Item -Path wrappers.zip
    ```

## Add tools to your project

With the wrapper scripts in place, you can start adding tools:

=== "Linux/Mac"
    ```bash
    # initialize a uv project in a (empty) directory without pyproject.toml
    ./pw uv init
    # add common tools to the project, including uv
    ./pw --add uv,ruff,pre-commit,px-utils
    # have uv create the virtual environment and install the dependencies
    ./pw uv sync
    # call the main script to show that the project is set up correctly
    ./pw uv run main.py
    ```

=== "Windows"
    ```powershell
    # initialize a uv project in a (empty) directory without pyproject.toml
    pw uv init
    # add common tools to the project, including uv
    pw --add uv,ruff,pre-commit,px-utils
    # have uv create the virtual environment and install the dependencies
    pw uv sync
    # call the main script to show that the project is set up correctly
    pw uv run main.py
    ```

## Lock tool versions

Lock the tool versions for reproducible builds:

=== "Linux/Mac"
    ```bash
    ./pw --lock
    ```

=== "Windows"
    ```powershell
    pw --lock
    ```

This creates a `pw.lock` file that pins every dependency to an exact version. Commit this file to version control.

## Define aliases

Aliases turn Pyprojectx into a lightweight task runner. Add them to your `pyproject.toml`:

```toml title="pyproject.toml"
[tool.pyprojectx.aliases]
test = "uv run pytest"
lint = "ruff check"
check = ["@lint", "@test"]
```

Now `./pw check` (or `px check`) runs lint followed by test. You can even use abbreviations -- `px c` is enough if no other alias starts with _c_.

See the full [alias documentation](/config/aliases) for composition, parameters, and more.

## Add to version control

When using Git:
```shell
git add pw pw.bat
git add pw.ps1 # optional
git update-index --chmod=+x pw
echo .pyprojectx/ >> .gitignore
```
For Windows users, having `pw.bat` is typically sufficient. `pw.ps1` can be handy for Powershell users when running commands containing special characters (like `<`), but this only works properly in recent Powershell versions.


## Install the `px` shortcut

You can copy a small script to `.pyprojectx` in your home directory.
When added to your _PATH_, you can replace `./pw` with the shorter `px`.
This also works from subdirectories: `../../pw` can also be replaced with `px`

=== "Linux/Mac"
    ```bash
    ./pw --install-px
    ```

=== "Windows"
    ```powershell
    pw --install-px
    ```

If you don't want to prefix every command with `px` or `./pw`, you [can activate a tool context](/config/tools#tool-context-activation).

## Next steps

- [Usage](/usage) -- CLI reference and common workflows
- [Configuration](/config/tools) -- configure tool contexts, aliases, and scripts
- [Recipes](/recipes) -- build scripts, CI/CD, Jupyter notebooks, and more
