from __future__ import annotations

from pathlib import Path

from project_dumper.renderer import build_document, line_broken, tree_to_list


def test_renderer_output_contains_sections(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()

    files = [Path("main.py"), Path("README.md")]
    contents = [
        (Path("main.py"), "print('hello')"),
        (Path("README.md"), "# Title"),
    ]
    tree_text = "repo\n└── main.py"

    doc = build_document(
        root=root,
        tree_text=tree_text,
        files=files,
        file_contents=contents,
        include_tree=True,
    )

    output = tmp_path / "dump.md"
    doc.save(output)
    text = output.read_text(encoding="utf-8")

    assert "Project Dump — repo" in text
    assert "Table of Contents" in text
    assert "This document is a read-only snapshot" in text
    assert "Directory Tree" in text
    assert tree_to_list(tree_text) in text
    assert "File List" in text
    assert "main.py" in text
    assert "File Contents" in text
    assert "File: main-py" in text
    assert "Path: main.py" in text
    assert "print('hello')" in text
