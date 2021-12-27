import os
import shutil
import sys
from pathlib import Path

from pyprojectx.wrapper.pw import BLUE, CYAN, DEFAULT_INSTALL_DIR, PYPROJECT_TOML, RESET


def initialize(options):
    return INIT_COMMANDS.get(options.cmd, show_help)(options)


def show_help(_):
    """Show this help message."""
    print(f"{BLUE}Available --init commands:{RESET}")
    for cmd, fn in INIT_COMMANDS.items():
        print(f"{CYAN}{cmd}{RESET}", fn.__doc__, file=sys.stderr)


def initialize_global(options):
    """Initialize the global pyprojectx setup in you home directory.
    Use '--init global --force' to overwrite.
    """
    global_dir = Path.home().joinpath(DEFAULT_INSTALL_DIR, "global")
    wrapper_dir = Path(__file__).parent.parent.joinpath("wrapper")
    os.makedirs(global_dir, exist_ok=True)

    target_pw = global_dir.joinpath("pw")
    if target_pw.exists() and "--force" not in options.cmd_args:
        print(f"{target_pw} {BLUE} already exists, use '--init global --force' to overwrite{RESET}")
        return

    shutil.copy2(wrapper_dir.joinpath("pw.py"), target_pw)
    extension = ".bat" if sys.platform.startswith("win") else ""
    shutil.copy2(wrapper_dir.joinpath(f"px{extension}"), global_dir.parent)
    shutil.copy2(wrapper_dir.joinpath(f"pxg{extension}"), global_dir.parent)
    target_toml = global_dir.joinpath(PYPROJECT_TOML)
    if not target_toml.exists():
        shutil.copy2(Path(__file__).with_name("global-template.toml"), target_toml)

    print(f"{BLUE}Pyprojectx scripts are installed in your home directory.")
    if sys.platform.startswith("win"):
        print(
            f"Add the scripts to your path, by adding\n"
            f"{RESET}{global_dir.parent.absolute()}\n"
            f"{BLUE}to the path environment variable."
        )
    else:
        print(
            f"Add the scripts to your PATH, f.e. by appending following to your shell's profile"
            f" ({RESET}~/.profile{BLUE}, {RESET}~/.zshrc{BLUE}, {RESET}~/..bashrc{BLUE}, ...):\n"
            f"{RESET}export PATH=$PATH:{global_dir.parent.absolute()}"
        )
        print(f"{BLUE}Execute {RESET}px --info -{BLUE} to see the available tools and aliases in your project.")
        print(f"Run {RESET}pxg --info -{BLUE} to see the available tools and aliases in the global pyprojectx.{RESET}")


INIT_COMMANDS = {
    "help": show_help,
    "global": initialize_global,
}
