# Configurable defaults

## Current working directory
You can change the default working directory for all commands by setting the `cwd` option.

Sensible values are `.` (the current directory) or `@PROJECT_DIR` (the directory containing _pyproject.toml_).

Defaults to `@PROJECT_DIR`

```toml
[tool.pyprojectx]
cwd = "."
```

Aliases can override the global cwd.


## Environment variables
You can set environment variables that will be added to the system environment when running a command:

```toml
[tool.pyprojectx]
env = { POETRY_VIRTUALENVS_PATH = "/data/poetry" }
```

Aliases can provide additional environment variables and/or override the global ones.

## Shell
You can change the os shell used to run commands. The shell can be defined globally, os specific or alias specific.

```toml
[tool.pyprojectx]
shell = "bash
[tool.pyprojectx.os.win]
shell = "pwsh.exe"
```

!!! danger "Specifying a shell changes variable substitution"
    Commands are converted into a single string and passed to the shell with the `-c` option,
    example: `bash -c "echo $PATH"`. This changes the variable substitution that is done by your os
    and can lead to unexpected results.

When you set a shell for os specific file operations, consider using [px-utils](https://github.com/pyprojectx/px-utils) instead.
```toml
[tool.pyprojectx.alias]
prepare = "pxmkdirs build generated"
copy = "pxcp src/**/*.py build/python"
move = "pxmv data/**/*.json build/data"
clean = "pxrm build generated"
```
