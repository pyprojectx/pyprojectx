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
Besides the `px` script, `pw --install-px` also copies other files:

* `pxg` script in `~/.pyprojectx`
* `pw` script and example `pyproject.toml` in `~/.pyprojectx/global`

`pxg` can be used as a lightweight [pipx](https://pypa.github.io/pipx/) to install tools globally.

Example usage: `pyproject.toml` contains by default [httpie](https://httpie.io/) so you can make http requests:
```shell
pxg http POST pie.dev/post hello=world
```

Uninstalling all global tools is just a matter of `rm -rf ~/.pyprojectx/global/.pyprojectx`
