import os
import shutil
import sys
from pathlib import Path

import userpath

from pyprojectx.log import logger
from pyprojectx.wrapper.pw import (
    BLUE,
    DEFAULT_INSTALL_DIR,
    RED,
    RESET,
)

HOME_DIR = Path(os.environ.get("PYPROJECTX_HOME_DIR", Path.home()))

DEFAULT_GLOBAL_CONFIG = """[tool.pyprojectx]
cwd = "."

[tool.pyprojectx.aliases]
"""


def install_px(options):
    """Install the global px and pxg scripts in your home directory."""
    install_dir = HOME_DIR / DEFAULT_INSTALL_DIR
    global_dir = install_dir / "global"
    wrapper_dir = Path(__file__).parent / "wrapper"
    logger.debug("creating global directory %s", global_dir)
    global_dir.mkdir(parents=True, exist_ok=True)

    target_pw = global_dir / "pw"
    shutil.copy2(wrapper_dir / "pw.py", target_pw)
    for file in wrapper_dir.glob("px*"):
        shutil.copy2(file, install_dir)

    if not (global_dir / "pyproject.toml").exists():
        with (global_dir / "pyproject.toml").open("w", encoding="utf-8") as f:
            f.write(DEFAULT_GLOBAL_CONFIG)
        print(
            f"{BLUE}Created a global pyproject.toml file in {RESET}{global_dir / 'pyproject.toml'}",
            file=sys.stderr,
        )

    print(
        f"{BLUE}Global Pyprojectx scripts are installed in your home directory. "
        f"You can now start all your commands with {RESET}px{BLUE} in any subdirectory of your project "
        f"instead of using {RESET}./pw{BLUE}. You can also use {RESET}pxg{BLUE} to run commands from "
        f"the global pyprojectx directory, f.e. {RESET}pxg uv init{BLUE} initialize a new Python project.",
        file=sys.stderr,
    )
    if options.cmd and "skip-path" in options.cmd:
        print(
            "Not adding the global pyprojectx directory to your PATH. You will need to add it manually.",
            file=sys.stderr,
        )
    else:
        ensure_path(global_dir)
    print(
        f"{BLUE}Run {RESET}px --info{BLUE} to see the available tools and aliases in your project.",
        file=sys.stderr,
    )
    print(
        f"Run {RESET}pxg --info{BLUE} to see the available tools and aliases in the global pyprojectx.{RESET}",
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
    except Exception:  # noqa: BLE001
        print(
            f"{global_path} {RED} could not be added automatically to PATH. You will need to add it manually{RESET}",
            file=sys.stderr,
        )
