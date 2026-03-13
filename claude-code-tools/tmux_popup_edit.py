#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
tmux_popup_edit - Open nvim in a tmux popup window and wait for it to exit.

A CLI wrapper that imitates nvim, but opens it in a tmux popup window
with all arguments forwarded to the actual nvim command. Blocks until
nvim exits and returns its exit code.

Usage:
    tmux_popup_edit [nvim args...]
    tmux_popup_edit -h|--help
    tmux_popup_edit -v|--version

Options:
    --help          Show this help message
    --version       Show version
    -w, --width     Popup width (default: 80%)
    -H, --height    Popup height (default: 90%)

Examples:
    tmux_popup_edit file.py
    tmux_popup_edit -p ~/.config/nvim/init.lua
    tmux_popup_edit -w 100 -h 50 server.py
"""

import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from shutil import which

__version__ = "1.0.0"


def is_in_tmux() -> bool:
    """Check if we're running inside a tmux session."""
    return "TMUX_PANE" in os.environ


def find_nvim() -> str:
    """Find the nvim executable path."""
    nvim_path = which("nvim")
    if not nvim_path:
        print("error: nvim not found in PATH", file=sys.stderr)
        sys.exit(1)
    return nvim_path


def main() -> int:
    args = sys.argv[1:]

    # Handle our own flags
    width = "80%"
    height = "90%"

    filtered_args = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--help":
            print(__doc__)
            return 0
        elif arg == "--version":
            print(f"tmux_popup_edit {__version__}")
            return 0
        elif arg in ("-w", "--width"):
            if i + 1 < len(args):
                width = args[i + 1]
                i += 1
        elif arg in ("-H", "--height"):
            if i + 1 < len(args):
                height = args[i + 1]
                i += 1
        else:
            filtered_args.append(arg)
        i += 1

    nvim_path = find_nvim()

    # If not in tmux, invoke nvim directly
    if not is_in_tmux():
        return subprocess.run([nvim_path] + filtered_args).returncode

    # Create a temporary file to signal completion and store exit code
    # Use a predictable pattern for cleanup
    temp_dir = Path(tempfile.gettempdir())
    signal_file = temp_dir / f"tmux_popup_edit_{os.getpid()}"

    # Build the nvim command with proper quoting
    nvim_cmd = shlex.join([nvim_path] + filtered_args)

    # Build a shell command that runs nvim, captures exit code, writes to file
    shell_cmd = f"{nvim_cmd}; echo $? > {shlex.quote(str(signal_file))}"

    # Build the tmux popup-window command
    cmd = [
        "tmux", "popup",
        "-w", width,
        "-h", height,
        "-E",  # Don't close the popup until command exits
        "bash", "-c", shell_cmd
    ]

    # Execute tmux popup
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"error: tmux popup failed: {e}", file=sys.stderr)
        return 1

    # Wait for the signal file to appear (nvim has exited)
    try:
        while not signal_file.exists():
            time.sleep(0.05)

        # Read the exit code
        exit_code = int(signal_file.read_text().strip())
        return exit_code
    except KeyboardInterrupt:
        # If user interrupts, return 130 (standard for SIGINT)
        return 130
    finally:
        # Clean up the signal file
        if signal_file.exists():
            signal_file.unlink()


if __name__ == "__main__":
    sys.exit(main())
