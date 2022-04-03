# Shortcut common commands with aliases
Aliases allow you to define shortcuts for common commands and simple shell scripts.

Tools that expose multiple scripts, also require aliases to make all scripts available via the `pw` wrapper script.

!!! info "`px` or `pw`?"
    This section assumes that you installed the [px utility script](/usage/#install-the-global-px-script).
    Otherwise, you need to replace `px` with `./pw` (Linux, Mac) or `.\pw` (Windows PowerShell).

## Defining shortcuts
You can avoid a lot of typing by aliasing commands that you use a lot. Example:
```toml
[tool.pyprojectx.aliases]
install = "poetry install"
run = "poetry run"
```

With above aliases, you can type `px install` instead of the usual `poetry install`. Depending on your other aliases,
this can be even shortened to `px i` (see [alias abbreviations](/config/aliases/#abbreviations)).

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
clean = "rd/s /q build generated"
```

Above `clean` alias will override the default one on Windows
(in fact on all operating systems where `sys.platform.startswith("win")==True`).

!!! note "Aliases are interpreted by the OS shell"

    The alias `show-path = "echo %PATH%"` will print the PATH environment variable on Windows, but will print
    literally `%PATH%` on another OS.

## Combining aliases
Use the `pw@` prefix to call alias from another alias.

```toml
[tool.pyprojectx.aliases]
unit-test = "poetry run pytest tests/unit"
integration-test = "poetry run pytest tests/integration"
test = "pw@unit-test && pw@integration-test"
```

`pw@` is substituted with the initial wrapper command + arguments.

So running `px -v test` will expand to
```
px -v poetry run pytest tests/unit && px -v  poetry run pytest tests/integration
```

## Tools and packages with multiple scripts
When installing multiple tools/packages together, or when using a tool that installs multiple scripts,
you can define aliases to expose additional scripts besides the main script.

By starting an alias with `@tool-name:`, where _tool-name_ is the key of a `[tool.pyprojectx]` entry, the alias always
runs in the context of the virtual environment that is created for `tool-name`.

```toml
[tool.pyprojectx]
# available scripts: flake8, pyflakes, black, ...
flake8 = ["flake8 ~=4.0", "flake8-black ~=0.3"]

[tool.pyprojectx.aliases]
# expose black that is installed together with flake8-black
black = "@flake8: black"
```

Now you can run black as usual:
```shell
px black --version
# black, 22.1.0 (compiled: yes)
```

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
    black = "black"
    [tool.pyprojectx.aliases]
    black-adder = "echo 'Field Marshal Haig is about to make yet another gargantuan effort to move his drinks cabinet six inches closer to Berlin.'"
    black = "@black: black"
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
