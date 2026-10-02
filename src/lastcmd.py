#!/usr/bin/env python3
"""Copy stdin to the terminal and to the system clipboard."""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Sequence


CLIPBOARD_BACKENDS: tuple[tuple[str, Sequence[str]], ...] = (
    ("wl-copy", ("wl-copy",)),
    ("xclip", ("xclip", "-selection", "clipboard")),
    ("xsel", ("xsel", "--clipboard", "--input")),
)


def find_clipboard_backend() -> tuple[str, Sequence[str]] | None:
    """Return the first available clipboard backend."""
    for name, command in CLIPBOARD_BACKENDS:
        if shutil.which(name):
            return name, command
    return None


def copy_to_clipboard(data: bytes) -> str:
    """Copy bytes to the system clipboard and return the backend name."""
    backend = find_clipboard_backend()
    if backend is None:
        raise RuntimeError(
            "No clipboard backend found. Install wl-clipboard, xclip, or xsel."
        )

    name, command = backend
    subprocess.run(command, input=data, check=True)
    return name


def main() -> int:
    """Read stdin, pass it through unchanged, and copy it to the clipboard."""
    data = sys.stdin.buffer.read()

    try:
        backend = copy_to_clipboard(data)
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        print(f"lastcmd: clipboard copy failed: {exc}", file=sys.stderr)
        return 1

    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    print(f"✓ copied to clipboard ({backend})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
