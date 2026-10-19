#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Pop up kitty+nvim, then paste the saved text into the original niri window."""

import fcntl
import json
import logging
import os
import shutil
import stat
import subprocess
import tempfile
import time
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

TERMINALS = {
    "kitty",
    "alacritty",
    "foot",
    "footclient",
    "org.wezfurlong.wezterm",
    "com.mitchellh.ghostty",
}
MIME = "text/plain;charset=utf-8"


def command(args, *, timeout=3, capture=False, **kwargs):
    # wl-copy forks a clipboard server: never give it an inherited output pipe
    # whose EOF subprocess.run would wait for after the parent has exited.
    return subprocess.run(
        args,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
        check=True,
        **kwargs,
    )


def focused_window(timeout=3) -> dict | None:
    result = command(
        ["niri", "msg", "-j", "focused-window"],
        capture=True,
        timeout=timeout,
    )
    return json.loads(result.stdout)


def notify(message):
    try:
        command(["notify-send", "nvim_insert", message], timeout=2)
    except (OSError, subprocess.SubprocessError):
        pass


@contextmanager
def instance_lock():
    runtime = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
    path = runtime / f"nvim-insert-{os.getuid()}.lock"
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if info.st_uid != os.getuid() or not stat.S_ISREG(info.st_mode):
            raise RuntimeError("Invalid lock file")
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.fchmod(fd, 0o600)
        yield
    finally:
        # Keep the inode: unlinking it would allow a second independent lock.
        os.close(fd)


@contextmanager
def diagnostic_log():
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    directory = root / "nvim-insert"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    handler = RotatingFileHandler(
        directory / "events.log",
        maxBytes=256 * 1024,
        backupCount=1,
        encoding="utf-8",
    )
    (directory / "events.log").chmod(0o600)
    handler.setFormatter(logging.Formatter("%(asctime)s pid=%(process)d %(message)s"))
    logger = logging.getLogger("nvim-insert")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    try:
        yield logger
    finally:
        logger.removeHandler(handler)
        handler.close()


def wait_for_focus(window_id):
    deadline = time.monotonic() + 2
    stable_since = None
    while (remaining := deadline - time.monotonic()) > 0:
        current = focused_window(timeout=min(3, remaining))
        now = time.monotonic()
        if current is not None and current["id"] == window_id:
            if stable_since is None:
                stable_since = now
            elif now - stable_since >= 0.1:
                return
        else:
            stable_since = None
        time.sleep(0.05)
    raise RuntimeError("Original window did not regain stable focus")


def verify_clipboard(data):
    result = command(
        ["wl-paste", "--no-newline", "--type", MIME],
        capture=True,
        timeout=10,
    )
    if result.stdout != data:
        raise RuntimeError("Clipboard changed or could not be verified")


def insert(logger):
    started = time.monotonic()
    stage = "target"
    directory = None
    path = None
    complete = False
    try:
        target = focused_window()
        if target is None:
            logger.info("stage=target result=no-window")
            return 0
        logger.info("stage=target window_id=%s", target["id"])

        directory = Path(tempfile.mkdtemp(prefix="nvim-insert-"))
        path = directory / "text.txt"
        path.touch(mode=0o600)
        stage = "editor"
        command(
            [
                "kitty",
                "--class",
                "floating-editor",
                "--",
                "nvim",
                "+startinsert",
                str(path),
            ],
            timeout=None,
        )
        data = path.read_text(encoding="utf-8").removesuffix("\n").encode("utf-8")
        if not data:
            complete = True
            logger.info("stage=editor result=empty")
            return 0

        stage = "clipboard"
        command(["wl-copy", "--type", MIME], input=data, timeout=10)
        verify_clipboard(data)
        logger.info("stage=clipboard result=verified bytes=%d", len(data))

        stage = "focus"
        command(["niri", "msg", "action", "focus-window", "--id", str(target["id"])])
        wait_for_focus(target["id"])

        stage = "pre-paste"
        verify_clipboard(data)
        current = focused_window()
        if current is None or current["id"] != target["id"]:
            raise RuntimeError("Focus changed before paste")

        stage = "keys"
        combo = (
            [29, 42, 47]
            if (target.get("app_id") or "").lower() in TERMINALS
            else [29, 47]
        )
        keys = [f"{key}:1" for key in combo] + [f"{key}:0" for key in reversed(combo)]
        env = os.environ.copy()
        env.setdefault("YDOTOOL_SOCKET", f"/run/user/{os.getuid()}/.ydotool_socket")
        try:
            command(["ydotool", "key", *keys], env=env)
        except (Exception, KeyboardInterrupt):
            try:
                releases = [f"{key}:0" for key in reversed(combo)]
                command(["ydotool", "key", *releases], env=env)
                logger.info("stage=keys-release result=sent")
            except (OSError, subprocess.SubprocessError, KeyboardInterrupt) as error:
                logger.error(
                    "stage=keys-release result=failed error=%s", type(error).__name__
                )
            raise
        complete = True
        logger.info("stage=keys result=sent insertion=unconfirmed")
        return 0
    except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 -- preserve text even on unexpected workflow failures
        # No command output or exception message: neither should leak body text.
        logger.error(
            "stage=%s result=failed error=%s returncode=%s recovery=%s",
            stage,
            type(error).__name__,
            getattr(error, "returncode", None),
            path,
        )
        recovery = f"\n已保存文字：{path}" if path is not None and path.exists() else ""
        notify(f"自动粘贴未完成；请手动恢复，避免重复插入。{recovery}")
        return 1
    finally:
        if complete and directory is not None:
            shutil.rmtree(directory)
        logger.info("stage=finish elapsed_ms=%.0f", (time.monotonic() - started) * 1000)


def main():
    os.umask(0o077)
    try:
        with instance_lock(), diagnostic_log() as logger:
            return insert(logger)
    except BlockingIOError:
        notify("已有编辑窗口或粘贴流程正在运行。")
        return 0
    except Exception:  # noqa: BLE001 -- surface initialization failures without leaking exception contents
        notify("nvim_insert 无法初始化锁或诊断日志。")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
