#!/usr/bin/env python3
"""Statusline for Claude Code - displays folder, git, model, time, and context info."""

import json
import os
import subprocess
import sys


def get_git_info(cwd: str) -> tuple[str | None, str | None]:
    """Get git branch and status counts. Returns (branch, status_str) or (None, None) if not a git repo."""
    try:
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
        )
        branch = result.stdout.strip() if result.returncode == 0 else ""

        if not branch:
            return None, None

        # Get status counts
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode != 0:
            return branch, None

        staged = 0
        modified = 0
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            # First char = index/staged status
            if line[0] in "MADRC":
                staged += 1
            # Second char = worktree status
            if len(line) > 1 and line[1] in "MADRC":
                modified += 1

        if staged == 0 and modified == 0:
            status_str = "clean"
        else:
            parts = []
            if staged > 0:
                parts.append(f"+{staged}")
            if modified > 0:
                parts.append(f"~{modified}")
            status_str = " ".join(parts)

        return branch, status_str

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None, None


def format_duration(ms: int | None) -> str:
    """Convert milliseconds to M:SS format."""
    if ms is None:
        return "0:00"
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def shorten_path(path: str) -> str:
    """Replace $HOME with ~ in path."""
    home = os.environ.get("HOME", "")
    if home and path.startswith(home):
        return "~" + path[len(home):]
    return path


def main():
    # Read JSON from stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("statusline error")
        return

    # Extract fields with fallbacks
    cwd = data.get("cwd", os.getcwd())

    model = data.get("model", {}) or {}
    model_name = model.get("display_name")

    cost = data.get("cost", {}) or {}
    duration_ms = cost.get("total_duration_ms")

    context = data.get("context_window", {}) or {}
    context_pct = context.get("used_percentage")

    # Get git info
    branch, status = get_git_info(cwd)

    # Build status line conditionally
    parts = [f"folder: {shorten_path(cwd)}"]

    if branch:
        parts.append(branch)
    if status:
        parts.append(status)

    if model_name:
        parts.append(model_name)

    if duration_ms:
        parts.append(format_duration(duration_ms))

    if context_pct is not None:
        parts.append(f"{context_pct}% context")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
