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
