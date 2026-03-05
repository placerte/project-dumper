from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

DUMP_FILE_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+-dump-\d{8}-\d{4}\.(md|pdf)$")


def find_dump_files(root: Path) -> list[Path]:
    """
    Find dump files matching the strict dump filename regex in `root`.

    Args:
        root: Directory to scan for dump artifacts.

    Returns:
        A list of matching file paths.
    """
    matches: list[Path] = []
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        if DUMP_FILE_PATTERN.match(entry.name):
            matches.append(entry)
    return matches


def clean_dump_files(root: Path, dry_run: bool) -> Iterable[Path]:
    """
    Delete dump files matching the strict regex, or report them in dry-run mode.

    Args:
        root: Directory to clean.
        dry_run: If True, do not delete files.

    Returns:
        An iterable of files that were removed or would be removed.
    """
    matches = find_dump_files(root)
    if dry_run:
        return matches

    for path in matches:
        path.unlink()
    return matches
