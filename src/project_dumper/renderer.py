from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Sequence

from simdoc import Doc


def heading(doc: Doc, text: str, level: int = 2) -> None:
    """Insert a heading into the document."""
    doc.h(level, text)


def paragraph(doc: Doc, text: str) -> None:
    """Insert a paragraph into the document."""
    doc.p(text)


def codeblock(doc: Doc, text: str, lang: str | None = None) -> None:
    """Insert a fenced code block into the document."""
    doc.code(text, lang=lang)


def line_broken(text: str) -> str:
    """Format text so Markdown preserves line breaks without code blocks."""
    return "  \n".join(text.splitlines())


def tree_to_list(tree_text: str) -> str:
    """Convert the ASCII tree to a Markdown unordered list."""
    lines = tree_text.splitlines()
    list_lines: list[str] = []
    for line in lines:
        if "── " not in line:
            depth = 0
            name = line.strip()
        else:
            prefix, name = line.split("── ", 1)
            depth = len(prefix) // 4
            name = name.strip()
        indent = "  " * depth
        list_lines.append(f"{indent}- {name}")
    return "\n".join(list_lines)


def sanitize_heading(text: str) -> str:
    """Normalize heading text for stable TOC anchors."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-")
    return normalized or "file"


def build_document(
    root: Path,
    tree_text: str,
    files: Sequence[Path],
    file_contents: Iterable[tuple[Path, str]],
    include_tree: bool,
) -> Doc:
    """
    Build a project dump document using simdoc.

    Args:
        root: Project root directory.
        tree_text: Prebuilt directory tree text.
        files: Ordered list of files included in the dump.
        file_contents: Iterable of (file_path, content) pairs in order.
        include_tree: Whether the directory tree should be included.

    Returns:
        The constructed simdoc Doc instance.
    """
    project_name = root.name
    doc = Doc()
    heading(doc, f"Project Dump — {project_name}", level=1)

    heading(doc, "Table of Contents")
    doc.toc(title=None)
    paragraph(
        doc,
        "\n".join(
            [
                "This document is a read-only snapshot of the project for review.",
                "Conventions:",
                "- Each file entry is labeled with its relative path.",
                "- File contents are shown as fenced code blocks.",
            ]
        ),
    )

    heading(doc, "Directory Tree")
    if include_tree:
        paragraph(doc, tree_to_list(tree_text))
    else:
        paragraph(doc, "Directory tree omitted (--no-tree).")

    heading(doc, "File List")
    file_list_text = "\n".join(str(path) for path in files)
    paragraph(doc, line_broken(file_list_text))

    heading(doc, "File Contents")
    for path, content in file_contents:
        sanitized = sanitize_heading(str(path))
        heading(doc, f"File: {sanitized}", level=3)
        paragraph(doc, f"Path: {path}")
        codeblock(doc, content)

    return doc
