from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import List, Set

from project_dumper.constants import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_EXCLUDE_EXTS,
    DEFAULT_MAX_BYTES,
)
from project_dumper.files import iter_files, read_text_file, add_line_numbers
from project_dumper.header import format_header
from project_dumper.tree import build_dir_tree
from project_dumper.gitignore import load_gitignore


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
        default=None,
        help="Output text file. If omitted, a name based on project and timestamp is generated.",
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
        default=DEFAULT_MAX_BYTES,
        help=f"Skip files larger than this size in bytes (default: {DEFAULT_MAX_BYTES:,}).",
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
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Ignores .gitignore (default: uses .gitignore if present"

    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    root = Path(args.root).resolve()

    gitignore_spec = None
    if not args.no_gitignore:
        gitignore_spec = load_gitignore(root)

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root path does not exist or is not a directory: {root}")

    if args.output is None:
        project_name = root.name
        timsestamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
        output = Path(f"{project_name}-dump-{timsestamp}.txt")
    else:
        output = Path(args.output)

    exclude_dirs: Set[str] = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir)
    exclude_exts: Set[str] = set(DEFAULT_EXCLUDE_EXTS) | {e.lower() for e in args.exclude_ext}
    include_exts: Set[str] | None = (
        {e.lower() for e in args.include_ext} if args.include_ext is not None else None
    )

    files = sorted(
        iter_files(
            root,
            exclude_dirs,
            exclude_exts,
            include_exts,
            args.max_bytes,
            gitignore_spec=gitignore_spec,
        ),
        key=lambda p: str(p.relative_to(root)),
    )

    header = format_header(root, include_exts, exclude_dirs, exclude_exts, gitignore_used=False)

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

