from __future__ import annotations

from typing import Set

# Directories we don't want to descend into by default.
DEFAULT_EXCLUDE_DIRS: Set[str] = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
}

# File extensions that are usually binary / not useful for LLM context.
DEFAULT_EXCLUDE_EXTS: Set[str] = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".bin",
    ".obj",
    ".o",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".zip",
    ".tar",
    ".gz",
    ".xz",
    ".7z",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
}

# Default maximum file size to include (in bytes).
DEFAULT_MAX_BYTES: int = 2_000_000

# Number of bytes sampled when detecting binary files.
BINARY_DETECTION_SAMPLE_SIZE: int = 8_000

