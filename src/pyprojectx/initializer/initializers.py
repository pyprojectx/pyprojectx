import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import tomli
import userpath

from pyprojectx.log import logger
from pyprojectx.wrapper.pw import (
    BLUE,
    CYAN,
    DEFAULT_INSTALL_DIR,
    PYPROJECT_TOML,
    RED,
    RESET,
)

SCRIPT_EXTENSION = ".bat" if sys.platform.startswith("win") else ""
SCRIPT_PREFIX = ".\\" if sys.platform.startswith("win") else "./"

HOME_DIR = Path(os.environ.get("PYPROJECTX_HOME_DIR", Path.home()))


def initialize(options):
    return INIT_COMMANDS.get(options.cmd, show_help)(options)


def show_help(_):
    """Show this help message."""
    print(f"{BLUE}Available --init commands:{RESET}", file=sys.stderr)
    for cmd, fn in INIT_COMMANDS.items():
        print(f"{CYAN}{cmd}{RESET}", fn.__doc__, file=sys.stderr)


def initialize_project(_):
    """Initialize pyprojectx setup in the current working directory.

    If pyproject.toml already exists and doesn't yet contain a tool.pyprojectx section,
    an example section will be appended.
    """
    _initialize_template("project-template.toml")
    _print_usage()


def initialize_poetry(options):
    """Initialize a poetry project in the current working directory, along with pyprojectx scripts."""
    logger.info("copying poetry.toml")
    shutil.copy2(Path(__file__).with_name("poetry.toml"), ".")
    _initialize_build_tool("poetry", options)


def initialize_pdm(options):
    """Initialize a PDM project in the current working directory, along with pyprojectx scripts."""
    _initialize_build_tool("pdm", options)


def _initialize_build_tool(tool, options):
    template = f"{tool}-template.toml"
    _initialize_template(template, toml_file=template)

    logger.info("installing %s...", tool)
    proc = subprocess.run(
        f"{SCRIPT_PREFIX}pw --toml {template} {tool} --version",
        shell=True,
        check=True,
        capture_output=True,
    )
    version = re.search(r"(\d+\.)+(\d+)", proc.stdout.decode("utf-8"))[0]
    old_requirement = f"{tool}>=1.1"
    new_requirement = f"{tool}=={version}"
    logger.info("setting version in %s : %s", PYPROJECT_TOML, new_requirement)
    _replace_in_file(old_requirement, new_requirement, template)
    subprocess.run(
        f"{SCRIPT_PREFIX}pw --toml {template} {tool} init " + " ".join(options.cmd_args), shell=True, check=True
    )
    logger.debug("appending template to %s...", PYPROJECT_TOML)
    with open(template) as src, open(PYPROJECT_TOML, "a") as dest:  # noqa PTH123
        dest.write(src.read())
    _print_usage()
    os.remove(template)  # noqa PTH123
    print(
        f"\n{BLUE}You can run all {CYAN}{tool}{BLUE} commands by typing {RESET}{SCRIPT_PREFIX}pw {BLUE} in front",
        file=sys.stderr,
    )
    print(f"Example: {RESET}{SCRIPT_PREFIX}pw {tool} update", file=sys.stderr)
    print(f"{BLUE}Or use the shorter aliases like {RESET}{SCRIPT_PREFIX}pw install {BLUE}and", file=sys.stderr)
    print(
        f"{RESET}{SCRIPT_PREFIX}pw run {BLUE}to install your project or run a script with {CYAN}{tool}{RESET}",
        file=sys.stderr,
    )


def _initialize_template(template_name, toml_file=PYPROJECT_TOML):
    wrapper_dir = Path(__file__).parent.parent.joinpath("wrapper")
    target_pw = Path("pw")
    if not target_pw.exists():
        logger.info("copying wrapper scripts")
        shutil.copy2(wrapper_dir.joinpath("pw.py"), target_pw)
        shutil.copy2(wrapper_dir.joinpath("pw.bat"), ".")
    else:
        logger.info("wrapper scripts already present")
    target_toml = Path(toml_file)
    template = Path(__file__).with_name(template_name)
    if not target_toml.exists():
        logger.info("copying %s template", template_name)
        shutil.copy2(template, target_toml)
    else:
        with target_toml.open("a+") as dst:
            toml_dict = tomli.load(dst)
            if not toml_dict.get("tool", {}).get("pyprojectx"):
                with template.open() as src:
                    logger.info("appending template to %s", toml_file)
                    dst.write(src.read())


def _replace_in_file(old, new, file):
    with open(file) as f:  # noqa PTH123
        text = f.read().replace(old, new)
    with open(file, "w") as f:  # noqa PTH123
        f.write(text)


def _print_usage():
    print(f"{BLUE}Pyprojectx scripts are installed in the current directory.", file=sys.stderr)
    print("You can add pw and pw.bat under version control if applicable.", file=sys.stderr)
    if sys.platform.startswith("win"):
        print(f"When using git, run {RESET}git add pw pw.bat && git update-index --chmod=+x pw'", file=sys.stderr)
    print(
        f"{BLUE}Run {RESET}{SCRIPT_PREFIX}pw --info -{BLUE}"
        f" to see the available tools and aliases in your project.{RESET}",
        file=sys.stderr,
    )


def initialize_global(options):
    """Initialize the global pyprojectx setup in your home directory.

    Use '--init global --force' to overwrite.
    """
    global_dir = HOME_DIR.joinpath(DEFAULT_INSTALL_DIR, "global")
    wrapper_dir = Path(__file__).parent.parent.joinpath("wrapper")
    logger.debug("creating global directory %s", global_dir)
    global_dir.mkdir(parents=True, exist_ok=True)

    target_pw = global_dir.joinpath("pw")
    if target_pw.exists() and "--force" not in options.cmd_args:
        print(f"{target_pw} {BLUE} already exists, use '--init global --force' to overwrite{RESET}", file=sys.stderr)
        return

    shutil.copy2(wrapper_dir.joinpath("pw.py"), target_pw)
    shutil.copy2(wrapper_dir.joinpath(f"px{SCRIPT_EXTENSION}"), global_dir.parent)
    shutil.copy2(wrapper_dir.joinpath(f"pxg{SCRIPT_EXTENSION}"), global_dir.parent)
    target_toml = global_dir.joinpath(PYPROJECT_TOML)
    if not target_toml.exists():
        shutil.copy2(Path(__file__).with_name("global-template.toml"), target_toml)

    print(f"{BLUE}Pyprojectx scripts are installed in your home directory.", file=sys.stderr)
    if "--skip-path" not in options.cmd_args:
        ensure_path(global_dir)
    print(
        f"{BLUE}Run {RESET}px --info -{BLUE} to see the available tools and aliases in your project.",
        file=sys.stderr,
    )
    print(
        f"Run {RESET}pxg --info -{BLUE} to see the available tools and aliases in the global pyprojectx.{RESET}",
        file=sys.stderr,
    )


def ensure_path(location: Path):
    global_path = str(location.parent.absolute())
    try:
        if userpath.in_current_path(global_path):
            print(f"{global_path} is already in PATH.", file=sys.stderr)
        else:
            userpath.append(global_path, "pyprojectx")
            print(f"{global_path} has been been added to PATH", file=sys.stderr)
        if userpath.need_shell_restart(global_path):
            print(
                " but you need to open a new terminal or re-login for this PATH change to take effect.", file=sys.stderr
            )
    except Exception:  # noqa BLE001
        print(
            f"{global_path} {RED} could not be added automatically to PATH. You will need to add it manually{RESET}",
            file=sys.stderr,
        )


INIT_COMMANDS = {
    "help": show_help,
    "project": initialize_project,
    "poetry": initialize_poetry,
    "pdm": initialize_pdm,
    "global": initialize_global,
}
