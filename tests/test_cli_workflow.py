from __future__ import annotations

from pathlib import Path

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
