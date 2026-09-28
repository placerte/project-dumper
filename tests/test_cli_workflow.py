from __future__ import annotations

from pathlib import Path

import pytest

from project_dumper import __version__
from project_dumper.cleaning import DUMP_FILE_PATTERN
from project_dumper.cli import main


def test_default_workflow_cleans_then_dumps(tmp_path: Path, monkeypatch) -> None:
    old_dump = tmp_path / "repo-dump-20260305-1044.md"
    old_dump.write_text("old", encoding="utf-8")

    project_file = tmp_path / "app.py"
    project_file.write_text("print('ok')", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    main([str(tmp_path)])

    assert not old_dump.exists()

    dump_files = [
        path for path in tmp_path.iterdir() if DUMP_FILE_PATTERN.match(path.name)
    ]
    assert len(dump_files) == 1


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"pytest {__version__}"


def test_update_command_reports_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "project_dumper.cli.update_executable",
        lambda current_version: f"updated {current_version}",
    )

    main(["update"])

    assert capsys.readouterr().out.strip() == f"updated {__version__}"
