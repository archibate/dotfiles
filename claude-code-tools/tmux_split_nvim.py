#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
tmux_split_nvim - Open nvim in a new tmux split pane.

A CLI wrapper that imitates nvim, but opens it in a new tmux split pane
with all arguments forwarded to the actual nvim command.

Usage:
    tmux_split_nvim [nvim args...]
    tmux_split_nvim -h|--help
    tmux_split_nvim -v|--version

Options:
    -h, --help      Show this help message
    -v, --version   Show version
    -H, --hsplit    Force horizontal split (panes side by side)
    -V, --vsplit    Force vertical split (panes stacked)

Examples:
    tmux_split_nvim file.py
    tmux_split_nvim -p ~/.config/nvim/init.lua
    tmux_split_nvim -H server.py client.py
"""

import os
import subprocess
import sys
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
            print(f"tmux_split_nvim {__version__}")
            return 0
        elif arg in ("-H", "--hsplit"):
            split_direction = "-h"
        elif arg == "-V":
            split_direction = "-v"
        elif arg == "--vsplit":
            split_direction = "-v"
        else:
            filtered_args.append(arg)

    # Check if we're in tmux
    if not is_in_tmux():
        print("error: not running inside tmux", file=sys.stderr)
        return 1

    nvim_path = find_nvim()

    # Build the command
    # tmux split-window [-v|-h] [-l size|-p percentage] command
    cmd = ["tmux", "split-window"]

    if split_direction:
        cmd.append(split_direction)

    # Add nvim with forwarded arguments
    cmd.append(nvim_path)
    cmd.extend(filtered_args)

    # Execute tmux split-window
    try:
        subprocess.run(cmd, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"error: tmux split-window failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
