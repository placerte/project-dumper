from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import Iterable, Sequence, Set

from project_dumper.clipboard import ClipboardResult, copy_file_to_clipboard
from project_dumper.cleaning import clean_dump_files
from project_dumper.constants import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_EXCLUDE_EXTS,
    DEFAULT_MAX_BYTES,
)
from project_dumper.files import add_line_numbers, iter_files, read_text_file
from project_dumper.gitignore import load_gitignore
from project_dumper.renderer import build_document
from project_dumper.tree import build_dir_tree


def add_dump_arguments(parser: argparse.ArgumentParser) -> None:
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
        help="Output file. If omitted, a name based on project and timestamp is generated.",
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
        help="Ignore .gitignore (default: uses .gitignore if present).",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Export PDF only (requires pandoc and xelatex).",
    )


def add_clean_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory to clean (default: current directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show files that would be deleted without removing them.",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    examples = (
        "Examples:\n"
        "  produm .\n"
        "  produm dump .\n"
        "  produm dump . --pdf\n"
        "  produm clean .\n"
        "  produm clean . --dry-run\n"
        "\n"
        "Default behavior:\n"
        "  produm <path> runs clean then dump."
    )
    base_parser = argparse.ArgumentParser(
        description="Dump a project into a single, LLM-friendly document.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_dump_arguments(base_parser)

    subcommand_parser = argparse.ArgumentParser(
        description="Dump or clean project artifacts.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = subcommand_parser.add_subparsers(dest="command")

    dump_parser = subparsers.add_parser("dump", help="Generate a project dump.")
    add_dump_arguments(dump_parser)

    clean_parser = subparsers.add_parser("clean", help="Remove prior dump artifacts.")
    add_clean_arguments(clean_parser)

    candidate_argv = list(argv) if argv is not None else sys.argv[1:]
    if candidate_argv and candidate_argv[0] in {"dump", "clean"}:
        return subcommand_parser.parse_args(candidate_argv)

    args = base_parser.parse_args(candidate_argv)
    setattr(args, "command", None)
    return args


def build_output_path(root: Path, output: str | None, pdf: bool) -> Path:
    if output is None:
        project_name = root.name
        timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
        suffix = ".pdf" if pdf else ".md"
        return Path(f"{project_name}-dump-{timestamp}{suffix}")

    output_path = Path(output)
    if pdf and output_path.suffix.lower() != ".pdf":
        return output_path.with_suffix(".pdf")
    return output_path


def gather_files(
    root: Path,
    exclude_dirs: Set[str],
    exclude_exts: Set[str],
    include_exts: Set[str] | None,
    max_bytes: int,
    use_gitignore: bool,
) -> list[Path]:
    gitignore_spec = None
    if use_gitignore:
        gitignore_spec = load_gitignore(root)

    return sorted(
        iter_files(
            root,
            exclude_dirs,
            exclude_exts,
            include_exts,
            max_bytes,
            gitignore_spec=gitignore_spec,
        ),
        key=lambda p: str(p.relative_to(root)),
    )


def build_file_contents(
    root: Path,
    files: Iterable[Path],
    with_line_numbers: bool,
) -> list[tuple[Path, str]]:
    contents: list[tuple[Path, str]] = []
    for path in files:
        rel = path.relative_to(root)
        content = read_text_file(path)
        if with_line_numbers:
            content = add_line_numbers(content)
        contents.append((rel, content))
    return contents


def run_dump(args: argparse.Namespace) -> Path:
    """Generate the project dump document and save it to disk."""
    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root path does not exist or is not a directory: {root}")

    output = build_output_path(root, args.output, args.pdf)

    exclude_dirs: Set[str] = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir)
    exclude_exts: Set[str] = set(DEFAULT_EXCLUDE_EXTS) | {
        e.lower() for e in args.exclude_ext
    }
    include_exts: Set[str] | None = (
        {e.lower() for e in args.include_ext} if args.include_ext is not None else None
    )

    files = gather_files(
        root,
        exclude_dirs,
        exclude_exts,
        include_exts,
        args.max_bytes,
        use_gitignore=not args.no_gitignore,
    )
    rel_files = [path.relative_to(root) for path in files]
    file_contents = build_file_contents(root, files, args.with_line_numbers)

    tree_text = build_dir_tree(root, exclude_dirs) if not args.no_tree else ""
    doc = build_document(
        root=root,
        tree_text=tree_text,
        files=rel_files,
        file_contents=file_contents,
        include_tree=not args.no_tree,
    )

    try:
        if args.pdf:
            doc.save_pdf(output)
        else:
            doc.save(output)
    except OSError as e:
        raise SystemExit(f"Error writing output file {output}: {e}")

    print(f"Wrote dump for {len(files)} files to {output}")
    clipboard_result = copy_dump_to_clipboard(output)
    if clipboard_result.success:
        print("Clipboard: copied dump file.")
    else:
        reason = f": {clipboard_result.message}" if clipboard_result.message else ""
        print(f"Warning: clipboard copy failed{reason}")
    return output


def copy_dump_to_clipboard(output: Path) -> ClipboardResult:
    """Copy the generated dump file to the clipboard."""
    return copy_file_to_clipboard(output)


def run_clean(args: argparse.Namespace) -> list[Path]:
    """Remove dump artifacts in the target directory (or preview in dry-run)."""
    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root path does not exist or is not a directory: {root}")

    try:
        removed = list(clean_dump_files(root, args.dry_run))
    except OSError as e:
        raise SystemExit(f"Error removing dump files in {root}: {e}")
    if args.dry_run:
        prefix = "Would remove"
    else:
        prefix = "Removed"

    for path in removed:
        rel = path.relative_to(root)
        print(f"{prefix}: {rel}")
    return removed


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""
    args = parse_args(argv)

    if args.command == "clean":
        run_clean(args)
        return
    if args.command == "dump":
        run_dump(args)
        return

    run_clean(
        argparse.Namespace(
            root=args.root,
            dry_run=False,
        )
    )
    run_dump(args)


if __name__ == "__main__":
    main()
