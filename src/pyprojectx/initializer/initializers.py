import os
import shutil
import sys
from pathlib import Path

import tomli

from pyprojectx.wrapper.pw import BLUE, CYAN, DEFAULT_INSTALL_DIR, PYPROJECT_TOML, RESET

SCRIP_EXTENSION = ".bat" if sys.platform.startswith("win") else ""
SCRIP_PREFIX = "" if sys.platform.startswith("win") else "./"


def initialize(options):
    return INIT_COMMANDS.get(options.cmd, show_help)(options)


def show_help(_):
    """Show this help message."""
    print(f"{BLUE}Available --init commands:{RESET}")
    for cmd, fn in INIT_COMMANDS.items():
        print(f"{CYAN}{cmd}{RESET}", fn.__doc__, file=sys.stderr)


def initialize_project(_):
    """Initialize pyprojectx setup in the current working directory.
    If pyproject.toml already exists and doesn't yet contain a tool.pyprojectx section,
    an example section will be appended.
    """
    wrapper_dir = Path(__file__).parent.parent.joinpath("wrapper")
    target_pw = Path("pw")
    if not target_pw.exists():
        shutil.copy2(wrapper_dir.joinpath("pw.py"), target_pw)
        shutil.copy2(wrapper_dir.joinpath("pw.bat"), ".")
    target_toml = Path(PYPROJECT_TOML)
    template = Path(__file__).with_name("project-template.toml")
    if not target_toml.exists():
        shutil.copy2(template, target_toml)
    else:
        with open(target_toml, "a+") as dst:
            toml_dict = tomli.load(dst)
            if not toml_dict.get("tool", {}).get("pyprojectx"):
                with open(template, "r") as src:
                    dst.write(src.read())

    print(f"{BLUE}Pyprojectx scripts are installed in the current directory.")
    print("You can add pw and pw.bat under version control if applicable.")
    if sys.platform.startswith("win"):
        print(f"When using git, run {RESET}git add pw pw.bat && git update-index --chmod=+x pw'")
    print(
        f"{BLUE}Run {RESET}{SCRIP_PREFIX}pw --info -{BLUE}"
        f" to see the available tools and aliases in your project.{RESET}"
    )


def initialize_global(options):
    """Initialize the global pyprojectx setup in your home directory.
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
    shutil.copy2(wrapper_dir.joinpath(f"px{SCRIP_EXTENSION}"), global_dir.parent)
    shutil.copy2(wrapper_dir.joinpath(f"pxg{SCRIP_EXTENSION}"), global_dir.parent)
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
        print(f"{BLUE}Run {RESET}px --info -{BLUE} to see the available tools and aliases in your project.")
        print(f"Run {RESET}pxg --info -{BLUE} to see the available tools and aliases in the global pyprojectx.{RESET}")


INIT_COMMANDS = {
    "help": show_help,
    "project": initialize_project,
    "global": initialize_global,
}
