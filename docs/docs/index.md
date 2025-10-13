<img alt="Pyprojectx" src="assets/px.png" style="background-color: white">
<i class="md-typeset md-header">
ALL-INCLUSIVE PYTHON PROJECTS
</i>

# Introduction
Pyprojectx makes it easy to create all-inclusive Python projects; no need to install any tools upfront,
not even Pyprojectx itself!

## Feature highlights
* Reproducible builds by treating tools and utilities as (versioned) dev-dependencies
* No global installs, everything is stored inside your project directory (like npm's _node_modules_)
* Bootstrap your entire build process with a small wrapper script (like Gradle's _gradlew_ wrapper)
* Configure shortcuts for routine tasks
* Simple configuration in _pyproject.toml_

Projects can be build/tested/used immediately without explicit installation nor initialization:
=== "Linux/Mac"
    ```bash
    git clone https://github.com/pyprojectx/px-demo.git
    # the demo project uses uv as build tool, but has branches for pdm and poetry
    cd px-demo
    ./pw build
    ```

=== "Windows"
    ```powershell
    git clone https://github.com/pyprojectx/px-demo.git
    # the demo project uses uv as build tool, but has branches for pdm and poetry
    cd px-demo
    pw build
    ```

![Clone and Build](assets/build.png)

## Installation
One of the key features is that there is no need to install anything explicitly (except a Python 3.9+ interpreter).

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
    # lock the tool versions for reproducible builds
    ./pw --lock
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
    # lock the tool versions for reproducible builds
    pw --lock
    ```

!!! tip "Tip: Add the wrapper scripts to version control"
    When using Git:
    ```shell
    git add pw pw.bat
    git add pw.ps1 # optional
    git update-index --chmod=+x pw
    echo .pyprojectx/ >> .gitignore
    ```
    For windows users, having `pw.bat` is typically sufficient. `pw.ps1` can be handy for Powershell users when running commands containing special characters (like `<`), but this only works properly in recent Powershell versions.


!!! tip "Tip: Install the `px` utility script"
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
