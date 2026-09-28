# produm

`produm` is a tiny CLI tool that flattens any small project into a single, LLM-friendly document. Useful when you want to show an entire codebase to ChatGPT or other LLMs without manually copying files. This was created for Python projects, but it could be generalized for other projects.

## Features
- Generates a single `.md` dump with:
  - Directory tree
  - File list
  - All text-based file contents
- Respects `.gitignore` (can be disabled)
- Skips binary files automatically
- Supports include/exclude rules
- Optional line numbers for code review and debugging
- Output name auto-generated unless specified
- Optional PDF export via Pandoc
- Clean command removes prior dump artifacts

## Installation

### Linux standalone app

Install the latest Linux x86_64 release without Python or a package manager:

```bash
curl -fsSL https://github.com/placerte/project-dumper/releases/latest/download/install.sh | sh
```

The installer writes `produm` to `~/.local/bin` by default. Set `INSTALL_DIR`
to choose another location. Update an installed standalone binary with:

```bash
produm update
```

### Python package

```bash
uv add produm
```
or
```bash
pip install produm
```

## Usage

### Basic

```bash
produm
```
or
```bash
produm .
```
will clean old dumps, then create a new dump file *from* and *in* the current directory.

### Subcommands

Dump only:

```bash
produm dump .
```

Clean only:

```bash
produm clean .
```

Dry-run cleaning:

```bash
produm clean . --dry-run
```

### Advanced

Specify output:

```bash
produm dump . -o dump.md
```


Only include Python files:

```bash
produm dump . --include-ext .py
```

Skip the directory tree:

```bash
produm dump . --no-tree
```

Export PDF only:

```bash
produm dump . --pdf
```

PDF export requires `pandoc` and `xelatex`.

## License
See [LICENSE](LICENSE)
