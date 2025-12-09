from __future__ import annotations

from pathlib import Path
from typing import List, Set


def build_dir_tree(root: Path, exclude_dirs: Set[str]) -> str:
    """
    Build a simple ASCII tree of directories and files under `root`,
    skipping any directory whose name is in `exclude_dirs`.
    """
    lines: List[str] = []

    root = root.resolve()
    root_name = root.name or str(root)

    lines.append(root_name)

    def walk(dir_path: Path, prefix: str = "") -> None:
        entries = sorted(
            [p for p in dir_path.iterdir()],
            key=lambda p: (p.is_file(), p.name.lower()),
        )
        total = len(entries)
        for idx, entry in enumerate(entries):
            is_last = idx == total - 1
            connector = "└── " if is_last else "├── "
            line = f"{prefix}{connector}{entry.name}"
            lines.append(line)
            if entry.is_dir() and entry.name not in exclude_dirs:
                new_prefix = prefix + ("    " if is_last else "│   ")
                walk(entry, new_prefix)

    walk(root)
    return "\n".join(lines)

