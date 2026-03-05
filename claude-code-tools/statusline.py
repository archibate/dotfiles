#!/usr/bin/env python3
"""Statusline for Claude Code - displays folder, git, model, time, and context info."""

import json
import os
import subprocess
import sys
from pathlib import Path

# Tokyo Night 256-color palette
C = {
    "reset": "\033[0m",
    "blue": "\033[38;5;111m",
    "cyan": "\033[38;5;117m",
    "green": "\033[38;5;150m",
    "yellow": "\033[38;5;179m",
    "red": "\033[38;5;203m",
    "purple": "\033[38;5;141m",
    "orange": "\033[38;5;215m",
    "comment": "\033[38;5;60m",
}


def c(text: str, color: str) -> str:
    """Wrap text with color code and reset."""
    return f"{C[color]}{text}{C['reset']}"


def context_color(pct: int) -> str:
    """Return color name based on context percentage."""
    if pct < 50:
        return "green"
    elif pct <= 80:
        return "orange"
    return "red"


def get_git_info(cwd: str) -> tuple[str | None, int, int]:
    """Get git branch and status counts. Returns (branch, staged, modified)."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
        )
        branch = result.stdout.strip() if result.returncode == 0 else ""

        if not branch:
            return None, 0, 0

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode != 0:
            return branch, 0, 0

        staged = 0
        modified = 0
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            if line[0] in "MADRC":
                staged += 1
            if len(line) > 1 and line[1] in "MADRC":
                modified += 1

        return branch, staged, modified

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None, 0, 0


def format_duration(ms: int | None) -> str:
    """Convert milliseconds to XhYmZs format. Hides hours/minutes when 0."""
    if ms is None:
        return "0s"
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h{minutes:02d}m{seconds:02d}s"
    if minutes > 0:
        return f"{minutes}m{seconds:02d}s"
    return f"{seconds}s"


def shorten_path(path: str) -> str:
    """Replace $HOME with ~ in path."""
    home = os.environ.get("HOME", "")
    if home and path.startswith(home):
        return "~" + path[len(home):]
    return path


def get_last_user_question(transcript_path: str | None, max_len: int = 40) -> str | None:
    """Get last user message from transcript, truncated to max_len chars."""
    if not transcript_path or not Path(transcript_path).exists():
        return None
    try:
        # Read last few lines of transcript JSONL
        result = subprocess.run(
            ["tail", "-50", transcript_path],
            capture_output=True,
            text=True,
            timeout=1,
        )
        if result.returncode != 0:
            return None

        lines = result.stdout.strip().split("\n")
        for line in reversed(lines):
            if not line:
                continue
            try:
                entry = json.loads(line)
                # Claude Code transcript format: {type: "user", message: {role: "user", content: ...}}
                if entry.get("type") != "user":
                    continue
                msg = entry.get("message", {})
                if msg.get("role") != "user":
                    continue
                content = msg.get("content", "")
                # Handle list content format (tool_result items)
                if isinstance(content, list):
                    texts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            texts.append(item.get("text", ""))
                        # Skip tool_result items
                    content = " ".join(texts)
                # Skip empty or whitespace-only content
                if not content or not content.strip():
                    continue
                # Truncate and clean
                content = content.strip().replace("\n", " ")
                if len(content) > max_len:
                    content = content[:max_len - 1] + "…"
                return content if content else None
            except json.JSONDecodeError:
                continue
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def format_status(staged: int, modified: int) -> str | None:
    """Format git status with colors."""
    if staged == 0 and modified == 0:
        return c("~", "green")
    parts = []
    if staged > 0:
        parts.append(c(f"+{staged}", "yellow"))
    if modified > 0:
        parts.append(c(f"~{modified}", "red"))
    return " ".join(parts)


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("statusline error")
        return

    cwd = data.get("cwd", os.getcwd())
    transcript_path = data.get("transcript_path")

    model = data.get("model", {}) or {}
    model_name = model.get("display_name")

    cost = data.get("cost", {}) or {}
    duration_ms = cost.get("total_duration_ms")

    context = data.get("context_window", {}) or {}
    context_pct = context.get("used_percentage")

    branch, staged, modified = get_git_info(cwd)

    sep = c("|", "comment")

    # Build status line conditionally with colors
    parts = [c(shorten_path(cwd), "blue")]

    if branch:
        parts.append(c(branch, "cyan"))
        status = format_status(staged, modified)
        if status:
            parts.append(status)

    if model_name:
        parts.append(c(model_name, "purple"))

    if duration_ms and duration_ms >= 30000:
        parts.append(c(format_duration(duration_ms), "yellow"))

    if context_pct is not None and context_pct > 0:
        pct_str = f"{context_pct}%"
        parts.append(c(pct_str, context_color(context_pct)))

    last_question = get_last_user_question(transcript_path)
    if last_question:
        parts.append(c(f"{last_question}", "comment"))

    print(f" {sep} ".join(parts))


if __name__ == "__main__":
    main()
