from __future__ import annotations

from pathlib import Path
from typing import Optional

import pathspec


def load_gitignore(root: Path) -> Optional[pathspec.PathSpec]:
    """
    Load .gitignore from root directory if it exists.
    Returns a PathSpec object or None.
    """
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        return None

    try:
        lines = gitignore_path.read_text().splitlines()
    except OSError:
        return None

    # Parse comments, blank lines, negation, directory patterns, etc.
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def matches_gitignore(spec: Optional[pathspec.PathSpec], path: Path, root: Path) -> bool:
    """
    Returns True if `path` should be ignored per gitignore.
    """
    if spec is None:
        return False

    rel = str(path.relative_to(root))
    return spec.match_file(rel)

