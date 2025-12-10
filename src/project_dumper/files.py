from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Set
from project_dumper.gitignore import matches_gitignore

from project_dumper.constants import BINARY_DETECTION_SAMPLE_SIZE


def is_probably_binary(path: Path, sample_size: int = BINARY_DETECTION_SAMPLE_SIZE) -> bool:
    """
    Heuristic: if the sampled bytes contain NUL, treat as binary.
    """
    try:
        with path.open("rb") as f:
            chunk = f.read(sample_size)
        if b"\x00" in chunk:
            return True
        return False
    except OSError:
        # If we can't read it, treat it as binary/unwanted
        return True


def iter_files(
    root: Path,
    exclude_dirs: Set[str],
    exclude_exts: Set[str],
    include_exts: Set[str] | None,
    max_bytes: int,
    gitignore_spec = None,
) -> Iterable[Path]:
    """
    Walk the project tree and yield files that match filtering rules.
    """
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter directories in-place so os.walk doesn't descend into them
        dirnames[:] = [
            d for d in dirnames
            if not matches_gitignore(gitignore_spec, Path(dirpath) / d, root)
            and d not in exclude_dirs
        ]
        for name in filenames:
            path = Path(dirpath) / name
            ext = path.suffix.lower()

            if include_exts is not None and ext not in include_exts:
                continue

            if ext in exclude_exts:
                continue

            try:
                size = path.stat().st_size
            except OSError:
                continue

            if size > max_bytes:
                continue

            if is_probably_binary(path):
                continue

            if matches_gitignore(gitignore_spec, path, root):
                continue

            if path.name == ".gitignore":
                continue

            yield path


def read_text_file(path: Path) -> str:
    """Read a text file with utf-8 + replacement fallback."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f"<<ERROR: could not read file {path}>>"


def add_line_numbers(text: str, start: int = 1) -> str:
    """
    Prefix each line with a line number.
    """
    lines = text.splitlines()
    width = len(str(start + len(lines) - 1))
    numbered: List[str] = [
        f"{str(i).rjust(width)} | {line}" for i, line in enumerate(lines, start)
    ]
    return "\n".join(numbered)

