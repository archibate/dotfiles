#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
tmux_split_nvim_block - Open nvim in a new tmux split pane and wait for it to exit.

A CLI wrapper that imitates nvim, but opens it in a new tmux split pane
with all arguments forwarded to the actual nvim command. Blocks until
nvim exits and returns its exit code.

Usage:
    tmux_split_nvim_block [nvim args...]
    tmux_split_nvim_block -h|--help
    tmux_split_nvim_block -v|--version

Options:
    -h, --help      Show this help message
    -v, --version   Show version
    -H, --hsplit    Force horizontal split (panes side by side)
    -V, --vsplit    Force vertical split (panes stacked)

Examples:
    tmux_split_nvim_block file.py
    tmux_split_nvim_block -p ~/.config/nvim/init.lua
    tmux_split_nvim_block -H server.py client.py
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
    split_direction = None  # None = let tmux decide based on window size

    filtered_args = []
    for arg in args:
        if arg in ("-h", "--help"):
            print(__doc__)
            return 0
        elif arg in ("-v", "--version"):
            print(f"tmux_split_nvim_block {__version__}")
            return 0
        elif arg in ("-H", "--hsplit"):
            split_direction = "-h"
        elif arg == "-V":
            split_direction = "-v"
        elif arg == "--vsplit":
            split_direction = "-v"
        else:
            filtered_args.append(arg)

    nvim_path = find_nvim()

    # If not in tmux, invoke nvim directly
    if not is_in_tmux():
        return subprocess.run([nvim_path] + filtered_args).returncode

    # Create a temporary file to signal completion and store exit code
    # Use a predictable pattern for cleanup
    temp_dir = Path(tempfile.gettempdir())
    signal_file = temp_dir / f"tmux_nvim_block_{os.getpid()}"

    # Build the nvim command with proper quoting
    nvim_cmd = shlex.join([nvim_path] + filtered_args)

    # Build a shell command that runs nvim, captures exit code, writes to file
    shell_cmd = f"{nvim_cmd}; echo $? > {shlex.quote(str(signal_file))}"

    # Build the tmux split-window command
    cmd = ["tmux", "split-window"]

    if split_direction:
        cmd.append(split_direction)

    cmd.extend(['bash', '-c'])
    cmd.append(shell_cmd)

    # Execute tmux split-window
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"error: tmux split-window failed: {e}", file=sys.stderr)
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
