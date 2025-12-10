# produm

`produm` is a tiny CLI tool that flattens any small project into a single, LLM-friendly text file. Useful when you want to show an entire codebase to ChatGPT or other LLMs without manually copying files. This was created for Python projects, but it could be generalized for other projects.

## Features
- Generates a single `.txt` dump with:
  - Directory tree
  - File list
  - All text-based file contents
- Respects `.gitignore` (can be disabled)
- Skips binary files automatically
- Supports include/exclude rules
- Optional line numbers for code review and debugging
- Output name auto-generated unless specified

## Installation

```bash
uv add produm
# or
pip install produm

