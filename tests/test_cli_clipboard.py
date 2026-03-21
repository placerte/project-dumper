from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from project_dumper import cli
from project_dumper.clipboard import ClipboardResult


def build_args(root: Path, output: Path) -> argparse.Namespace:
    return argparse.Namespace(
        root=str(root),
        output=str(output),
        pdf=False,
        include_ext=None,
        exclude_dir=[],
        exclude_ext=[],
        max_bytes=10_000_000,
        no_tree=True,
        with_line_numbers=False,
        no_gitignore=True,
    )


def test_run_dump_copies_to_clipboard_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "file.txt").write_text("hello", encoding="utf-8")
    output = tmp_path / "out.md"

    captured: dict[str, Path] = {}

    def fake_copy(path: Path) -> ClipboardResult:
        captured["path"] = path
        return ClipboardResult(True, None)

    monkeypatch.setattr(cli, "copy_file_to_clipboard", fake_copy)

    result = cli.run_dump(build_args(root, output))

    assert result == output
    assert output.exists()
    assert captured["path"] == output

    stdout = capsys.readouterr().out
    assert "Wrote dump" in stdout
    assert "Clipboard: copied dump file." in stdout


def test_run_dump_clipboard_failure_is_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "file.txt").write_text("hello", encoding="utf-8")
    output = tmp_path / "out.md"

    def fake_copy(path: Path) -> ClipboardResult:
        return ClipboardResult(False, "no clipboard")

    monkeypatch.setattr(cli, "copy_file_to_clipboard", fake_copy)

    result = cli.run_dump(build_args(root, output))

    assert result == output
    assert output.exists()

    stdout = capsys.readouterr().out
    assert "Wrote dump" in stdout
    assert "Warning: clipboard copy failed: no clipboard" in stdout
