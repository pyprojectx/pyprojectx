# Shortcut common commands with aliases

Aliases allow you to define shortcuts for common commands and simple shell scripts.

!!! info "`px` or `pw`?"

    This section assumes that you installed the [px utility script](/usage#install-the-global-px-script).
    Otherwise, you need to replace `px` with `./pw` (Linux, Mac) or `pw` (Windows PowerShell).


## Defining shortcuts

You can avoid a lot of typing by aliasing commands that you use a lot. Example:

```toml
[tool.pyprojectx.aliases]
install = "poetry install"
run = "poetry run"
```

With above aliases, you can type `px install` instead of the usual `poetry install`. Depending on your other aliases,
this can be even shortened to `px i` (see [alias abbreviations](/config/aliases#abbreviations)).

All arguments are passed to the underlying command or script,
making `px run my-script --foo` equivalent to `poetry run my-script --foo`.

## Shell scripts

Shell scripts can also be aliased:

```toml
[tool.pyprojectx.aliases]
prepare = "mkdir build && mkdir generated"
clean = "rm -rf build generated"
```

You can override aliases for a specific OS:

```toml
[tool.pyprojectx.os.win.aliases]
clean = "rd /s /q build generated"
```

Above `clean` alias will override the default one on Windows
(in fact on all operating systems where `sys.platform.startswith("win")==True`).

!!! tip "Tip: use px-utils for common file operations"

    Use [px-utils](https://github.com/pyprojectx/px-utils) to create, copy, move, delete, ... files and directories cross-platform.
    ```toml
    [tool.pyprojectx.os.win.aliases]
    clean = "pxrm build generated"
    ```

!!! note "Aliases are interpreted by the OS shell"

    The alias `show-path = "echo %PATH%"` will print the PATH environment variable on Windows, but will print
    literally `%PATH%` on another OS.

## Combining aliases

Use the `@` prefix to call an alias or [script](/config/scripts) from another alias.

```toml
[tool.pyprojectx.aliases]
unit-test = "pdm run pytest tests/unit"
integration-test = "pdm run pytest tests/integration"
test = ["@unit-test && @integration-test"]
# a list of commands behaves the same as when combined with '&&'
build = [
    "@install",
    "@test",
    "@pdm build",
]
```

`[pw]@` is substituted with the initial wrapper command + arguments.

So running `px -v test` will expand to

```
px -v poetry run pytest tests/unit && px -v  poetry run pytest tests/integration
```

## Alias configuration

Besides simple commands, aliases provide some configuration options:

```toml
notebook = { cmd = 'jupyter lab', ctx = 'jupyter', env = { JUPYTERLAB_DIR = "docs" } }
```

- `cmd`: the command to run
- `ctx`: the tool context in which the command is run; defaults to `main`
- `env`: additional environment variables to set
  - `cwd`: the working directory in which the command is run; defaults to _@PROJECT_DIR_, the directory containing
    _pyproject.toml_. This default ensures that commands can be run from any subdirectory of the project.
    Use _@PROJECT_DIR/subdir_ to run the command in a subdirectory of the project.
- `shell`: the shell used to run the command, overrides the default shell of the tool context

!!! note "Default CWD changed in 2.0.0"

    Prior to Pyprojectx 2.0.0, aliases where always executed in the current working directory.
    As of 2.0.0, aliases run by default in the root directory of the project (where _pyproject.toml_ is located),
    unless explicitly overridden with the `cwd` option.


## Abbreviations

To run an alias, you only have to type the portion of the alias name that uniquely identifies the alias within
the project. So we don't have to type the complete name if we can use a shorter version.
As a bonus Pyprojectx also supports camel case to abbreviate an alias name.

When you define an alias named either `foo-bar` or `fooBar`, then following commands are equivalent
(provided they don't match any other alias):

```shell
px foo-bar
px fooBar
px fooB
px fBar
px fB
px f
```

!!! caution "An alias can shadow other commands"

    Abbreviations come with the cost that an alias will shadow other non-alias commands when the alias' name
    starts with that command. For example:
    ```toml
    [tool.pyprojectx]
    main = ["black"]
    [tool.pyprojectx.aliases]
    black-adder = "echo 'Field Marshal Haig is about to make yet another gargantuan effort to move his drinks cabinet six inches closer to Berlin.'"
    black = "black"
    ```
    Here it would not be possible to use the `black` formatter without explicitly exposing it with the second alias.

!!! tip "Tip: Abbreviations as cli hints"

    When you don't remember the exact alias to run, just type the first letter(s) and `px` will refresh your memory 😁
    ```shell
    px c
    # 'c' is ambiguous
    # Candidates are:
    # clean, clean-all, check
    ```
    Or run `px -i` to list all available aliases and tools.
