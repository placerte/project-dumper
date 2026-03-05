from __future__ import annotations

from pathlib import Path

from project_dumper.cleaning import clean_dump_files, find_dump_files


def test_cleaning_deletes_only_matching_files(tmp_path: Path) -> None:
    valid_files = [
        "repo-dump-20260305-1044.md",
        "repo-dump-20260304-1812.pdf",
    ]
    invalid_files = [
        "repo-dump-latest.md",
        "repo-dump-2026.md",
        "repo_dump_20260305.md",
        "notes.md",
    ]

    for name in valid_files + invalid_files:
        (tmp_path / name).write_text("x", encoding="utf-8")

    removed = list(clean_dump_files(tmp_path, dry_run=False))
    removed_names = {path.name for path in removed}

    assert set(valid_files) == removed_names
    for name in invalid_files:
        assert (tmp_path / name).exists()


def test_cleaning_dry_run_does_not_delete(tmp_path: Path) -> None:
    target = tmp_path / "repo-dump-20260305-1044.md"
    target.write_text("x", encoding="utf-8")

    removed = list(clean_dump_files(tmp_path, dry_run=True))
    assert removed == [target]
    assert target.exists()


def test_find_dump_files(tmp_path: Path) -> None:
    target = tmp_path / "repo-dump-20260305-1044.pdf"
    target.write_text("x", encoding="utf-8")

    (tmp_path / "notes.md").write_text("x", encoding="utf-8")

    matches = find_dump_files(tmp_path)
    assert matches == [target]
