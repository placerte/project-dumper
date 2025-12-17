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
will create the dump file *from* and *in* the current directory.

### Advanced

Specify output:

```bash
produm . -o dump.txt
```


Only include Python files:

```bash
produm . --include-ext .py
```

Skip the directory tree:

```bash
produm . --no-tree
```

### Feature Wish List

- [ ] ```produm --clean .``` or ```produm --clean``` or ```produm -c```: cleans the current directory of all dump files (.txt with "-dump-" in filename) 
- [ ] Advanced option flag (or default?) ```produm -w``` or ```produm -wc``` overwrite and clean. 

## License
See [LICENSE](LICENSE)
