from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "lastcmd.py"

spec = importlib.util.spec_from_file_location("lastcmd", MODULE_PATH)
assert spec is not None
assert spec.loader is not None
lastcmd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lastcmd)


def test_output_is_forwarded_unchanged(monkeypatch, capsys):
    data = b"line 1\nline 2\n"
    captured = {}

    def fake_copy(value):
        captured["data"] = value
        return "test-backend"

    monkeypatch.setattr(lastcmd, "copy_to_clipboard", fake_copy)
    monkeypatch.setattr("sys.stdin", __import__("io").TextIOWrapper(
        __import__("io").BytesIO(data),
        encoding="utf-8",
    ))

    class FakeStdout:
        def __init__(self):
            self.buffer = __import__("io").BytesIO()

        def flush(self):
            pass

    fake_stdout = FakeStdout()
    monkeypatch.setattr("sys.stdout", fake_stdout)

    result = lastcmd.main()

    assert result == 0
    assert captured["data"] == data
    assert fake_stdout.buffer.getvalue() == data


def test_copy_failure_still_forwards_output(monkeypatch):
    data = b"important output\n"

    def fake_copy(_value):
        raise RuntimeError("clipboard unavailable")

    monkeypatch.setattr(lastcmd, "copy_to_clipboard", fake_copy)
    monkeypatch.setattr("sys.stdin", __import__("io").TextIOWrapper(
        __import__("io").BytesIO(data),
        encoding="utf-8",
    ))

    class FakeStdout:
        def __init__(self):
            self.buffer = __import__("io").BytesIO()

        def flush(self):
            pass

    fake_stdout = FakeStdout()
    monkeypatch.setattr("sys.stdout", fake_stdout)

    result = lastcmd.main()

    assert result == 1
    assert fake_stdout.buffer.getvalue() == data


def test_backend_detection_prefers_wayland(monkeypatch):
    monkeypatch.setattr(lastcmd.shutil, "which", lambda name: "/usr/bin/" + name)
    name, command = lastcmd.find_clipboard_backend()
    assert name == "wl-copy"
    assert command == ("wl-copy",)


def test_clipboard_backend_is_called_with_exact_bytes(monkeypatch):
    calls = {}

    monkeypatch.setattr(
        lastcmd,
        "find_clipboard_backend",
        lambda: ("test", ("fake-copy",)),
    )

    def fake_run(command, *, input, check):
        calls["command"] = command
        calls["input"] = input
        calls["check"] = check
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(lastcmd.subprocess, "run", fake_run)

    assert lastcmd.copy_to_clipboard(b"hello\x00world") == "test"
    assert calls == {
        "command": ("fake-copy",),
        "input": b"hello\x00world",
        "check": True,
    }
