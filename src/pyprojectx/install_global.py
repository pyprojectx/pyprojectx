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

SCRIPT_EXTENSION = ".bat" if sys.platform.startswith("win") else ""

HOME_DIR = Path(os.environ.get("PYPROJECTX_HOME_DIR", Path.home()))


def install_px(options):
    """Install the global px and pxg scripts in your home directory."""
    global_dir = HOME_DIR.joinpath(DEFAULT_INSTALL_DIR, "global")
    wrapper_dir = Path(__file__).parent.joinpath("wrapper")
    logger.debug("creating global directory %s", global_dir)
    global_dir.mkdir(parents=True, exist_ok=True)

    target_pw = global_dir.joinpath("pw")
    if target_pw.exists() and not options.force_install:
        raise Warning(f"{target_pw} {BLUE} already exists, use '--install-px --force-install' to overwrite{RESET}")

    shutil.copy2(wrapper_dir.joinpath("pw.py"), target_pw)
    shutil.copy2(wrapper_dir.joinpath(f"px{SCRIPT_EXTENSION}"), global_dir.parent)
    shutil.copy2(wrapper_dir.joinpath(f"pxg{SCRIPT_EXTENSION}"), global_dir.parent)

    print(
        f"{BLUE}Global Pyprojectx scripts are installed in your home directory. "
        "You can now start all your commands with 'px' in any subdirectory of your project instead of using './pw'",
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
