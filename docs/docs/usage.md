# Usage

## CLI
```
--8<-- "docs/usage.txt"
```

## Common workflows

### Running a tool for the first time
When you run a tool that isn't installed yet, Pyprojectx automatically creates its virtual environment and installs all requirements:

```bash
px ruff check
# first run: installs ruff, then runs the check
# subsequent runs: ruff is already available, runs immediately
```

### Adding a new tool
Use `--add` to add tools to `pyproject.toml` in one step:

```bash
./pw --add httpie
./pw http pie.dev/get
```

### Upgrading tools (re-locking)
When using a lock file, upgrade all tools to the latest compatible version by combining `--lock` with `--force-install`:

```bash
./pw --lock -f
```

This resolves fresh versions, recreates the virtual environments, and updates the `pw.lock` file.

### Forcing reinstallation
If a virtual environment gets corrupted or you want to ensure a clean state:

```bash
./pw --force-install ruff check
# or reinstall a specific context without running a command
./pw -f --install-context main
```

## Install the global `px` script
Pyprojectx provides a small `px` script that delegates everything to the `pw` wrapper script.
The `pw` script is searched for in the current working directory and its parents.

When added to your _PATH_, you can replace `./pw` with the shorter `px`.
This also works from subdirectories: `../../pw` can also be replaced with `px`

To install:

=== "Linux/Mac"
    ```bash
    ./pw --install-px
    ```

=== "Windows"
    ```powershell
    pw --install-px
    ```

## Global tools
Besides the `px` script, `pw --install-px` also installs the `pxg` script.

`pxg` can be used as a lightweight [pipx](https://pypa.github.io/pipx/) to install/run tools globally. It provides a default `uv`, f.e. `pxg uv --help` will show the help.

Example: make http requests with [httpie](https://httpie.io/):
```shell
pxg --add httpie
pxg http POST pie.dev/post hello=world
```

The global setup can be configured in _~/.pyprojectx/global/pyproject.toml_.

Uninstalling all global tools is just a matter of removing the global directory:
```shell
rm -rf ~/.pyprojectx/global/.pyprojectx
```
