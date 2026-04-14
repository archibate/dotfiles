#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Pop up a kitty+nvim editor, then type the content at the cursor."""

import os
import subprocess
import tempfile


def type_text(text: str):
    """Type text at current cursor position via clipboard paste."""
    if not text:
        return

    for selection in ["primary", "clipboard"]:
        subprocess.run(
            ["xclip", "-selection", selection],
            input=text.encode(),
            check=True,
        )
    subprocess.run(
        ["xdotool", "key", "--clearmodifiers", "shift+Insert"],
        check=True,
    )


def main():
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="nvim-insert-")
    os.close(fd)
    try:
        subprocess.run(
            ["kitty", "--class", "floating-editor", "--", "nvim", "+startinsert", path],
            check=True,
        )
        with open(path) as f:
            text = f.read()
        # Strip single trailing newline that nvim adds
        if text.endswith("\n"):
            text = text[:-1]
        type_text(text)
    finally:
        os.unlink(path)


if __name__ == "__main__":
    main()
