# Release 0.2.0

## Title
produm 0.2.0

## Summary
This release switches the renderer to simdoc, adds clean/dump subcommands with
the new default workflow, and introduces optional PDF export.

## Highlights
- Simdoc-based document generation with TOC and file section headings
- `produm clean` command with strict dump-file matching and dry-run
- `produm dump --pdf` for PDF export via Pandoc

## Breaking Changes
- Output format default is now Markdown (`.md`) instead of `.txt`
- CLI default behavior now cleans then dumps

## Requirements
- PDF export requires `pandoc` and `xelatex`

## Testing
- `uv run --with simdoc --with pytest pytest`
