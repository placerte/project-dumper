#!/usr/bin/env python3
"""
project_dump.py

Dump a code project into a single text file, with:

1) A human/LLM-readable header explaining the structure.
2) A directory tree of the project.
3) The contents of all selected files, each with a clear header.

Designed to be easy to later package as a PyPI CLI.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
from typing import Iterable, List, Set

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

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dump a project into a single, LLM-friendly text file."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory of the project (default: current directory).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="project_dump.txt",
        help="Output text file (default: project_dump.txt).",
    )
    parser.add_argument(
        "--include-ext",
        nargs="*",
        default=None,
        metavar="EXT",
        help=(
            "Only include files with these extensions (e.g. --include-ext .py .md .txt). "
            "If omitted, includes all non-binary files except excluded extensions."
        ),
    )
    parser.add_argument(
        "--exclude-dir",
        nargs="*",
        default=[],
        metavar="DIR",
        help="Additional directory names to exclude (on top of built-in defaults).",
    )
    parser.add_argument(
        "--exclude-ext",
        nargs="*",
        default=[],
        metavar="EXT",
        help="Additional file extensions to exclude (on top of built-in defaults).",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=2_000_000,
        help="Skip files larger than this size in bytes (default: 2,000,000).",
    )
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="Do not include the directory tree in the output.",
    )
    parser.add_argument(
        "--with-line-numbers",
        action="store_true",
        help="Include line numbers in file contents.",
    )
    return parser.parse_args()


def is_probably_binary(path: Path, sample_size: int = 8000) -> bool:
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


def build_dir_tree(root: Path, exclude_dirs: Set[str]) -> str:
    """
    Build a simple ASCII tree of directories and files.
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


def iter_files(
    root: Path,
    exclude_dirs: Set[str],
    exclude_exts: Set[str],
    include_exts: Set[str] | None,
    max_bytes: int,
) -> Iterable[Path]:
    """
    Walk the project tree and yield files that match filtering rules.
    """
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter directories in-place so os.walk doesn't descend into them
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for name in filenames:
            path = Path(dirpath) / name

            ext = path.suffix.lower()

            if include_exts is not None:
                if ext not in include_exts:
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

            yield path


def format_header(
    root: Path,
    include_exts: Set[str] | None,
    exclude_dirs: Set[str],
    exclude_exts: Set[str],
) -> str:
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    lines = [
        "# PROJECT DUMP FOR LLM / CODE REVIEW",
        "",
        f"Generated at: {now}",
        f"Project root: {root.resolve()}",
        "",
        "Document structure:",
        "1. This header section (what you are reading now).",
        "2. A directory tree of the project (if enabled).",
        "3. The contents of each included file, in deterministic order.",
        "",
        "Conventions:",
        "- Each file starts with a header line like:",
        "    ==== FILE: relative/path/to/file.py ==== ",
        "- File contents follow immediately after the header.",
        "",
        "LLM instructions (suggested):",
        "- Treat this as a *read-only* snapshot of the project.",
        "- When referencing code, mention the file path and line(s) if possible.",
        "- If you propose changes, explain them in terms of specific files/sections.",
        "",
        "Filtering applied:",
        f"- Excluded directory names: {sorted(exclude_dirs)}",
        f"- Excluded file extensions: {sorted(exclude_exts)}",
    ]
    if include_exts is None:
        lines.append("- Included extensions: ALL non-binary files (minus excluded ext).")
    else:
        lines.append(f"- Included extensions (whitelist): {sorted(include_exts)}")

    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    return "\n".join(lines)


def read_text_file(path: Path) -> str:
    # Use utf-8 with fallback.
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f"<<ERROR: could not read file {path}>>"


def add_line_numbers(text: str, start: int = 1) -> str:
    lines = text.splitlines()
    width = len(str(start + len(lines) - 1))
    numbered = [f"{str(i).rjust(width)} | {line}" for i, line in enumerate(lines, start)]
    return "\n".join(numbered)


def main() -> None:
    args = parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output)

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root path does not exist or is not a directory: {root}")

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir)
    exclude_exts = set(DEFAULT_EXCLUDE_EXTS) | {e.lower() for e in args.exclude_ext}
    include_exts = (
        {e.lower() for e in args.include_ext} if args.include_ext is not None else None
    )

    files = sorted(
        iter_files(root, exclude_dirs, exclude_exts, include_exts, args.max_bytes),
        key=lambda p: str(p.relative_to(root)),
    )

    header = format_header(root, include_exts, exclude_dirs, exclude_exts)

    tree_str = ""
    if not args.no_tree:
        tree_str = "DIRECTORY TREE\n" + "-" * 80 + "\n"
        tree_str += build_dir_tree(root, exclude_dirs)
        tree_str += "\n\n" + "=" * 80 + "\n\n"

    result_lines: List[str] = []
    result_lines.append(header)
    if tree_str:
        result_lines.append(tree_str)

    # Files section summary
    result_lines.append("FILES INCLUDED")
    result_lines.append("-" * 80)
    for f in files:
        rel = f.relative_to(root)
        result_lines.append(str(rel))
    result_lines.append("")
    result_lines.append("=" * 80)
    result_lines.append("")

    # Now dump each file with its own header + contents
    for f in files:
        rel = f.relative_to(root)
        result_lines.append(f"==== FILE: {rel} ====")
        result_lines.append("")
        content = read_text_file(f)
        if args.with_line_numbers:
            content = add_line_numbers(content)
        result_lines.append(content)
        result_lines.append("")  # blank line between files

    text = "\n".join(result_lines)

    try:
        output.write_text(text, encoding="utf-8")
    except OSError as e:
        raise SystemExit(f"Error writing output file {output}: {e}")

    print(f"Wrote dump for {len(files)} files to {output}")


if __name__ == "__main__":
    main()

