from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Set


def format_header(
    root: Path,
    include_exts: Set[str] | None,
    exclude_dirs: Set[str],
    exclude_exts: Set[str],
) -> str:
    """
    Build the top-of-file header that explains structure + instructions for the LLM.
    """
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

