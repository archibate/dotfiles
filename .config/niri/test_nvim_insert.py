"""Isolated regression tests: never connect to the desktop or clipboard."""

import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "nvim_insert",
    Path(__file__).with_name("nvim_insert.py"),
)
editor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(editor)


class Clock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="nvim-insert-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = []
        self.notices = []
        self.saved = "你好\nsecond line\n"
        self.clipboard = b""
        self.target = {"id": 7, "app_id": "kitty"}
        self.focus = 7
        self.focus_reads = 0
        self.failure = None
        self.overwrite = False
        self.drift = False
        self.lost = False
        self.no_window = False
        self.clock = Clock()
        self.environ = patch.dict(
            os.environ,
            {
                "XDG_RUNTIME_DIR": str(self.root),
                "XDG_STATE_HOME": str(self.root / "state"),
            },
        )
        self.environ.start()
        self.addCleanup(self.environ.stop)

    def command(self, args, **kwargs):
        self.calls.append((args, kwargs))
        output = b""
        if args[0] == "kitty":
            Path(args[-1]).write_text(self.saved, encoding="utf-8")
        if self.failure == args[0]:
            raise subprocess.CalledProcessError(1, args, stderr=b"PRIVATE BODY")
        if self.failure == "timeout" and args[0] == "ydotool":
            raise subprocess.TimeoutExpired(args, 3)
        if args[0] == "wl-copy":
            self.clipboard = kwargs["input"]
        elif args[0] == "wl-paste":
            output = self.clipboard
        elif args[0] == "niri":
            if "focus-window" in args:
                self.focus_reads = 0
                self.focus = None if self.lost else 7
                if self.overwrite:
                    self.clipboard = b"another writer"
            else:
                self.focus_reads += 1
                if self.drift and self.focus_reads >= 4:
                    self.focus = 99
                current = (
                    None
                    if self.no_window or self.focus is None
                    else {
                        "id": self.focus,
                        "app_id": self.target["app_id"],
                    }
                )
                import json

                output = json.dumps(current).encode()
        return subprocess.CompletedProcess(args, 0, stdout=output)

    def run_workflow(self):
        real_mkdtemp = tempfile.mkdtemp
        old_umask = os.umask(0o077)
        try:
            with (
                patch.object(editor, "command", side_effect=self.command),
                patch.object(editor, "notify", side_effect=self.notices.append),
                patch.object(editor.time, "monotonic", self.clock.monotonic),
                patch.object(editor.time, "sleep", self.clock.sleep),
                patch.object(
                    editor.tempfile,
                    "mkdtemp",
                    side_effect=lambda **kw: real_mkdtemp(dir=self.root, **kw),
                ),
            ):
                return editor.main()
        finally:
            os.umask(old_umask)

    def keys(self):
        return [args for args, _ in self.calls if args[0] == "ydotool"]

    def recovery(self):
        return list(self.root.glob("nvim-insert-*/text.txt"))

    def test_unicode_multiline_terminal_and_cleanup(self):
        self.target["app_id"] = "KiTtY"
        self.assertEqual(self.run_workflow(), 0)
        self.assertEqual(self.clipboard, "你好\nsecond line".encode())
        self.assertEqual(
            self.keys(),
            [["ydotool", "key", "29:1", "42:1", "47:1", "47:0", "42:0", "29:0"]],
        )
        self.assertFalse(self.recovery())
        self.assertFalse(any("--primary" in args for args, _ in self.calls))
        log = (self.root / "state/nvim-insert/events.log").read_text()
        self.assertNotIn("你好", log)
        self.assertIn("insertion=unconfirmed", log)
        self.assertGreaterEqual(self.clock.now, 0.1)

    def test_steam_uses_regular_paste(self):
        self.target["app_id"] = "steam"
        self.assertEqual(self.run_workflow(), 0)
        self.assertEqual(
            self.keys(), [["ydotool", "key", "29:1", "47:1", "47:0", "29:0"]]
        )

    def test_empty_cancel_has_no_clipboard_or_keys(self):
        self.saved = ""
        self.assertEqual(self.run_workflow(), 0)
        self.assertFalse(self.keys())
        self.assertFalse(any(args[0] == "wl-copy" for args, _ in self.calls))
        self.assertFalse(self.recovery())

    def test_no_target_does_not_launch_editor(self):
        self.no_window = True
        self.assertEqual(self.run_workflow(), 0)
        self.assertEqual([args[0] for args, _ in self.calls], ["niri"])

    def test_overwrite_aborts_before_keys_and_preserves_text(self):
        self.overwrite = True
        self.assertEqual(self.run_workflow(), 1)
        self.assertFalse(self.keys())
        self.assertEqual(self.recovery()[0].read_text(), self.saved)
        self.assertTrue(self.notices)

    def test_focus_drift_aborts_before_keys(self):
        self.drift = True
        self.assertEqual(self.run_workflow(), 1)
        self.assertFalse(self.keys())
        self.assertTrue(self.recovery())

    def test_missing_window_is_bounded(self):
        self.lost = True
        self.assertEqual(self.run_workflow(), 1)
        self.assertFalse(self.keys())
        self.assertLessEqual(self.clock.now, 2.1)
        self.assertTrue(self.recovery())

    def test_command_failures_preserve_saved_text_without_retry(self):
        for tool in ("kitty", "wl-copy", "wl-paste", "ydotool", "timeout"):
            with self.subTest(tool=tool):
                self.failure = tool
                self.calls.clear()
                self.assertEqual(self.run_workflow(), 1)
                self.assertTrue(self.recovery())
                paste_attempts = [
                    args
                    for args in self.keys()
                    if any(key.endswith(":1") for key in args)
                ]
                self.assertLessEqual(len(paste_attempts), 1)
                self.assertTrue(
                    all(path.read_text() == self.saved for path in self.recovery())
                )
                log = (self.root / "state/nvim-insert/events.log").read_text()
                self.assertNotIn("PRIVATE BODY", log)
                self.assertNotIn("你好", log)

    def test_duplicate_instance_cannot_launch_or_copy(self):
        with editor.instance_lock():
            self.assertEqual(self.run_workflow(), 0)
        self.assertFalse(self.calls)
        self.assertTrue(self.notices)
        self.assertEqual(self.run_workflow(), 0)

    def test_partial_key_timeout_releases_keys_without_repeating_paste(self):
        pressed = set()
        original = self.command

        def partial_send(args, **kwargs):
            if args[0] != "ydotool":
                return original(args, **kwargs)
            self.calls.append((args, kwargs))
            for event in args[2:]:
                key, down = event.split(":")
                if down == "1":
                    pressed.add(key)
                    if key == "47":
                        raise subprocess.TimeoutExpired(args, 3)
                else:
                    pressed.discard(key)
            return subprocess.CompletedProcess(args, 0)

        with patch.object(self, "command", side_effect=partial_send):
            self.assertEqual(self.run_workflow(), 1)
        self.assertFalse(pressed)
        self.assertEqual(len(self.keys()), 2)
        self.assertEqual(self.keys()[1], ["ydotool", "key", "47:0", "42:0", "29:0"])
        self.assertTrue(self.recovery())

    def test_recovery_permissions(self):
        self.failure = "wl-copy"
        self.assertEqual(self.run_workflow(), 1)
        path = self.recovery()[0]
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(
            (self.root / "state/nvim-insert").stat().st_mode & 0o777, 0o700
        )
        self.assertEqual(
            (self.root / "state/nvim-insert/events.log").stat().st_mode & 0o777, 0o600
        )

    def test_unstable_focus_never_counts_as_stable(self):
        clock = Clock()

        def alternating_focus(timeout):
            return {"id": 7 if round(clock.now / 0.05) % 2 == 0 else 99}

        with (
            patch.object(editor, "focused_window", side_effect=alternating_focus),
            patch.object(editor.time, "monotonic", clock.monotonic),
            patch.object(editor.time, "sleep", clock.sleep),
            self.assertRaises(RuntimeError),
        ):
            editor.wait_for_focus(7)


class BoundaryTests(unittest.TestCase):
    def test_real_cli_with_isolated_tools_and_forking_clipboard_server(self):
        import sys

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools = root / "bin"
            tools.mkdir()
            source = (
                f"#!{sys.executable}\n"
                + r"""
import json, os, sys, time
from pathlib import Path
tool = Path(sys.argv[0]).name
root = Path(os.environ['NVIM_INSERT_FIXTURE'])
if tool == 'niri':
    if sys.argv[-1] == 'focused-window':
        print(json.dumps({'id': 7, 'app_id': 'kitty'}))
elif tool == 'kitty':
    Path(sys.argv[-1]).write_text('隔离测试\nsecond line\n')
elif tool == 'wl-copy':
    assert sys.argv[1:] == ['--type', 'text/plain;charset=utf-8']
    (root / 'clipboard').write_bytes(sys.stdin.buffer.read())
    if os.fork() == 0:
        time.sleep(0.6)
        os._exit(0)
elif tool == 'wl-paste':
    assert sys.argv[1:] == ['--no-newline', '--type', 'text/plain;charset=utf-8']
    sys.stdout.buffer.write((root / 'clipboard').read_bytes())
elif tool == 'ydotool':
    (root / 'keys').write_text(json.dumps(sys.argv[1:]))
elif tool == 'notify-send':
    (root / 'notification').write_text(json.dumps(sys.argv[1:]))
else:
    raise RuntimeError(tool)
"""
            )
            for name in (
                "niri",
                "kitty",
                "wl-copy",
                "wl-paste",
                "ydotool",
                "notify-send",
            ):
                path = tools / name
                path.write_text(source)
                path.chmod(0o700)
            env = os.environ.copy()
            env.update(
                {
                    "PATH": str(tools),
                    "NVIM_INSERT_FIXTURE": str(root),
                    "XDG_RUNTIME_DIR": str(root),
                    "XDG_STATE_HOME": str(root / "state"),
                    "TMPDIR": str(root),
                }
            )
            result = subprocess.run(
                [sys.executable, editor.__file__],
                env=env,
                capture_output=True,
                timeout=3,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            import json

            self.assertEqual(
                json.loads((root / "keys").read_text()),
                ["key", "29:1", "42:1", "47:1", "47:0", "42:0", "29:0"],
            )
            self.assertEqual(
                (root / "clipboard").read_bytes(), "隔离测试\nsecond line".encode()
            )
            self.assertFalse(list(root.glob("nvim-insert-*/text.txt")))
            self.assertFalse((root / "notification").exists())

    def test_clipboard_server_never_inherits_capture_pipes(self):
        with patch.object(editor.subprocess, "run") as run:
            editor.command(["wl-copy"], input=b"text", timeout=10)
        self.assertEqual(run.call_args.kwargs["stdout"], subprocess.DEVNULL)
        self.assertEqual(run.call_args.kwargs["stderr"], subprocess.DEVNULL)
        self.assertEqual(run.call_args.kwargs["timeout"], 10)

    def test_real_timeout_is_bounded(self):
        import sys

        with self.assertRaises(subprocess.TimeoutExpired):
            editor.command(
                [sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.05
            )

    def test_lock_rejects_symlink(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict(os.environ, {"XDG_RUNTIME_DIR": directory}),
        ):
            target = Path(directory) / "target"
            target.touch()
            (Path(directory) / f"nvim-insert-{os.getuid()}.lock").symlink_to(target)
            with self.assertRaises(OSError), editor.instance_lock():
                self.fail("symlink accepted")

    def test_log_rotation_is_bounded_and_private(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict(os.environ, {"XDG_STATE_HOME": directory}),
        ):
            old_umask = os.umask(0o077)
            try:
                with editor.diagnostic_log() as logger:
                    for _ in range(700):
                        logger.info("stage=test %s", "x" * 1000)
                files = list((Path(directory) / "nvim-insert").glob("events.log*"))
                self.assertEqual(len(files), 2)
                for path in files:
                    self.assertLess(path.stat().st_size, 256 * 1024)
                    self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            finally:
                os.umask(old_umask)


if __name__ == "__main__":
    unittest.main()
