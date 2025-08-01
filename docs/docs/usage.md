# Usage

## CLI
```
--8<-- "docs/usage.txt"
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
Besides the `px` script, `pw --install-px` also copies adds the `pxg`.

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
