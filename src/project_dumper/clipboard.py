from __future__ import annotations

from dataclasses import dataclass
import os
import platform
import subprocess
from pathlib import Path


@dataclass(frozen=True)
class ClipboardResult:
    """Result of a clipboard copy attempt."""

    success: bool
    message: str | None = None


def copy_file_to_clipboard(path: Path) -> ClipboardResult:
    """Attempt to copy a file reference to the system clipboard."""
    resolved = path.resolve()
    if not resolved.exists() or not resolved.is_file():
        return ClipboardResult(False, f"File not found: {resolved}")

    system = platform.system()
    if system == "Darwin":
        return _copy_file_macos(resolved)
    if system == "Windows":
        return _copy_file_windows(resolved)
    if system == "Linux":
        return _copy_file_linux(resolved)
    return ClipboardResult(False, f"Unsupported OS: {system}")


def _copy_file_macos(path: Path) -> ClipboardResult:
    escaped = str(path).replace('"', '\\"')
    script = f'set the clipboard to {{POSIX file "{escaped}"}}'
    return _run_command(["osascript", "-e", script], None)


def _copy_file_windows(path: Path) -> ClipboardResult:
    escaped = str(path).replace("'", "''")
    script = (
        "$path = '{path}';"
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$collection = New-Object System.Collections.Specialized.StringCollection;"
        "$collection.Add($path) | Out-Null;"
        "[System.Windows.Forms.Clipboard]::SetFileDropList($collection)"
    ).format(path=escaped)
    return _run_command(
        ["powershell", "-NoProfile", "-STA", "-Command", script],
        None,
    )


def _copy_file_linux(path: Path) -> ClipboardResult:
    if "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ:
        return ClipboardResult(False, "Clipboard unavailable: DISPLAY not set")
    uri = f"{path.resolve().as_uri()}\n"
    return _run_command(
        ["xclip", "-selection", "clipboard", "-t", "text/uri-list"],
        uri,
    )


def _run_command(
    command: list[str],
    input_text: str | None,
    timeout_s: float | None = 5.0,
) -> ClipboardResult:
    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_s,
        )
    except FileNotFoundError:
        return ClipboardResult(False, f"Clipboard tool not found: {command[0]}")
    except OSError as exc:
        return ClipboardResult(False, f"Clipboard command failed: {exc}")
    except subprocess.TimeoutExpired:
        return ClipboardResult(False, "Clipboard command timed out")

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        return ClipboardResult(False, f"Clipboard command failed: {detail}")

    return ClipboardResult(True, None)
