#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Pop up kitty+nvim, then paste the saved text into the original niri window."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


def focused_window() -> dict | None:
    result = subprocess.run(
        ["niri", "msg", "-j", "focused-window"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def main():
    target = focused_window()
    if target is None:
        return

    with tempfile.TemporaryDirectory(prefix="nvim-insert-") as directory:
        path = Path(directory) / "text.txt"
        path.touch(mode=0o600)
        subprocess.run(
            ["kitty", "--class", "floating-editor", "--", "nvim", "+startinsert", str(path)],
            check=True,
        )
        text = path.read_text().removesuffix("\n")

    if not text:
        return

    for selection in ([], ["--primary"]):
        subprocess.run(["wl-copy", *selection], input=text.encode(), check=True)

    subprocess.run(
        ["niri", "msg", "action", "focus-window", "--id", str(target["id"])],
        check=True,
    )
    for _ in range(20):
        time.sleep(0.05)
        current = focused_window()
        if current is not None and current["id"] == target["id"]:
            break
    else:
        raise RuntimeError("Original window is unavailable; text is on the clipboard.")

    env = os.environ.copy()
    env.setdefault("YDOTOOL_SOCKET", f"/run/user/{os.getuid()}/.ydotool_socket")
    subprocess.run(
        ["ydotool", "key", "42:1", "110:1", "110:0", "42:0"],  # Shift+Insert
        env=env, check=True,
    )


if __name__ == "__main__":
    main()
