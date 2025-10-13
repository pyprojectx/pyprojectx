Release v3.3.1 (2025-10-13)
----------------------------
### Features & Improvements
- update uv to 0.9.2

Release v3.3.0 (2025-10-13)
----------------------------
### Features & Improvements
- Added _pw.ps1_ for better Windows PowerShell support
- `--upgrade` will only upgrade existing pw* wrapper scripts
- Permanently dropped support for Python 3.8

Release v3.2.9 (2025-08-11)
----------------------------
### Features & Improvements
- update uv to 0.8.8

Release v3.2.8 (2025-08-11)
----------------------------
### Bug Fixes
- #157 uv default tool context does not work if any other pyprojectx configuration is present

Release v3.2.7 (2025-08-01)
----------------------------
### Features & Improvements
- #156 omit uv warning and prompt when running with --lock

Release v3.2.6 (2025-08-01)
----------------------------
### Features & Improvements
- #154 omit uv warning and prompt in first run

Release v3.2.5 (2025-08-01)
----------------------------
### Features & Improvements
- #83 ./pw --upgrade should do the upgrade itself instead of printing instructions
- #119 add a way to update px/pxg

Release v3.2.4 (2025-06-18)
----------------------------
### Features & Improvements
- Use uv to build pyprojectx itself instead of PDM

Release v3.2.3 (2025-05-12)
----------------------------
### Bug Fixes
- #149 uv install script fallback is broken on macOS

Release v3.2.2 (2025-04-17)
----------------------------
### Bug Fixes
- #146 uv install script fallback method is not triggered when ensurepip is unavailable

### Documentation
- #148 improve uv and px-demo documentation

Release v3.2.1 (2025-04-16)
----------------------------
### Bug Fixes
- #143 error when installing pyprojectx on ubuntu if ensurepip is not available

Release v3.2.0 (2025-04-11)
----------------------------
### Features & Improvements
- #139 reduce the noise when terminating a command with Ctrl+C
- #140 use uv to manage pyprojectx venvs instead of the standard venv package

Release v3.1.5 (2025-01-20)
----------------------------
### Bug Fixes
- #137 the version of uv used by pyprojectx should not use the project's requires-python version

Release v3.1.4 (2025-01-20)
----------------------------
### Features & Improvements
- bump uv to uv 0.5.21

Release v3.1.3 (2024-11-18)
----------------------------
### Bug Fixes
- fix post-install actions that run an alias command

Release v3.1.2 (2024-11-15)
----------------------------
### Features & Improvements
- #131 creating an alias for a script with the same name gives errors
- #130 scripts_ctx isn't optimal and needs two venvs

Release v3.1.1 (2024-11-13)
----------------------------
### Features & Improvements
- update to uv 0.5.1

Release v3.1.0 (2024-11-13)
----------------------------
### Features & Improvements
- #127 easy initialisation of a uv project
- #126 make scripts_dir work with a venv

Release v3.0.9 (2024-11-07)
----------------------------
### Features & Improvements
- #116 expand/substitute environment variables in requirements
- #117 improve error output

Release v3.0.6 (2024-11-05)
----------------------------
### Bug Fixes
- #112 generated lock file does not respect the python version markers
- #120 uv fails to install python 3.13 when using python 3.12

Release v3.0.5 (2024-08-22)
----------------------------
### Bug Fixes
- #114 prerelease is not propagated when locking dependencies

Release v3.0.4 (2024-08-05)
----------------------------
### Features & Improvements
- revert constraint on python >=3.9 back to >=3.8

Release v3.0.3 (2024-08-03)
----------------------------
### Features & Improvements
- #110 add lock-python-version configuration option

Release v3.0.2 (2024-07-08)
----------------------------
### Bug Fixes
- #108 preserve line endings in pw.lock file on windows
- #109 show useful error output when --lock fails instead of crashing

Release v3.0.1 (2024-07-03)
----------------------------
### Features & Improvements
- Generate platform independent pw.lock files
- Pyprojectx initialization of a clean project is up to 10x faster!
- #95 use uv instead of pip
- #104 support requirements from a pyproject.toml file or a text file with `-r`
- #105 allow installing prerelease versions of tools with `prerelease = "allow"`
- Dropped support for Python 3.8!

Release v2.2.1 (2024-06-26)
----------------------------
### Features & Improvements
- #100 add --clean option to cleanup virtual environments

Release v2.2.0 (2024-06-25)
----------------------------
### Bug Fixes
- #98 existing tool virtual environment is reused even if pw.lock changed

Release v2.1.9 (2024-06-13)
----------------------------
### Bug Fixes
- #96 fix locking of pyprojectx's own dependencies

Release v2.1.6 (2024-03-11)
----------------------------
### Bug Fixes
- #90 fix PowerShell activate script when symlinks are allowed on Windows

Release v2.1.5 (2024-03-11)
----------------------------
### Features & Improvements
- use an informative prompt when activating a tool context virtual environment

### Bug Fixes
- #90 activate script doesn't work in windows PowerShell

Release v2.1.4 (2024-03-11)
----------------------------
### Bug Fixes
- #90 activate script doesn't work on cygwin

Release v2.1.2 (2024-03-08)
----------------------------
### Features & Improvements
- update pip when installing a tool context virtual environment

### Bug Fixes
- #90 activate script seems to be broken on windows
- #91 crashes on windows when symlinks are not allowed

### Documentation
- fixed windows development instructions in README.md

Release v2.1.1 (2024-03-07)
----------------------------
### Bug Fixes
- #89 Fix px install on Windows for git bash usage

Release v2.1.0 (2024-03-04)
----------------------------
### Features & Improvements
- #23 Make tool contexts "activatable" so that all tools are available
- #86 Make is easier to update all locked tool dependencies

Release v2.0.8 (2024-01-31)
----------------------------
### Features & Improvements
- #80 add support to create a project virtual environment

Release v2.0.7 (2024-01-25)
----------------------------
### Features & Improvements
- #76 --lock also installs non-lockable tool contexts

Release v2.0.6 (2024-01-17)
----------------------------
### Bug Fixes
- #75 locking loops forever when the post-install action is an alias

Release v2.0.5 (2024-01-17)
----------------------------
### Bug Fixes
- #72 locking does not execute post-install scripts

Release v2.0.4 (2024-01-17)
----------------------------
### Bug Fixes
- #70 incorrect hash in lock file

Release v2.0.3 (2024-01-16)
----------------------------
### Features & Improvements
- #59 px should have an init command that adds the pw script to the current folder

Release v2.0.2 (2024-01-10)
----------------------------
### Bug Fixes
- #68 pxg commands don't run in the current directory

Release v2.0.1 (2024-01-05)
----------------------------
### Features & Improvements
- #63 install multiple tools together in one add command
- Documentation for 2.0

### Bug Fixes
- #62 fix --install-px

Release v2.0.0 (2024-01-03)
----------------------------
### Features & Improvements
- #55 Optional locking of all tool dependencies
- #54 CLI option to add a tool to a context
- #52 Support for running Python scripts
- #50 Group tools in one virtual environment
- #46 Allow to specify the working directory for commands
- #27 Set alias interpreter explicitly
- #24 Command to install tool explicitly

### Bug Fixes
- #48 Executing a tool directly (without alias) assumes that the extension is always .exe on windows

Release v1.0.0b5 (2023-06-19)
----------------------------
### Features & Improvements
- Make aliases more readable by supporting lists of commands

Release v1.0.0b4 (2023-05-07)
----------------------------
### Features & Improvements
- Add CLI option that prints upgrade instructions
- Lock all dependencies in pyproject.toml to ensure that all future installs from pypi.org won't be broken by a dependency release
- Switch to PDM as build backend

Release v1.0.0b1 (2023-04-09)
----------------------------
### Bug Fixes
- Preserve quotes around command arguments when running an alias.

Release v0.9.9 (2022-03-14)
----------------------------
### Features & Improvements
- Automatically add the global scripts to the PATH when running "pw --init global"
- Moved pyprojectx to its own github organization
- Published full documentation on https://pyprojectx.github.io

Release v0.8.7 (2022-02-17)
----------------------------
### Features & Improvements
- Re-install a tool when its post-install script has changed.

Release v0.8.6 (2022-02-17)
----------------------------
### Features & Improvements
- Support post-install scripts that are executed after a tool is installed.

Release v0.8.5 (2022-01-14)
----------------------------
### Bug Fixes
- Display help when running pw without any option or command.

Release v0.8.4 (2022-01-10)
----------------------------
### Features & Improvements
- Allow aliases to be abbreviated when invoked
- Make cmd a non-mandatory CLI argument so that --init and --info can be used without a dummy command.

Release v0.8.3 (2021-12-28)
----------------------------
First official release.
