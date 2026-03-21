# AGENTS.md

### LLM Context Blocks

These files contain reusable instructions and workflows
that may be relevant when working in this repository.

<!-- agmod:start -->

- llm/agent_executor_instructions_v_1.md
- llm/code_style.md
- llm/progress_tracker.md
- llm/python_toolbox.md
- llm/sessions_logger.md
- llm/textual_resources.md
- llm/textual_toolbox.md
- llm/user-persona.md

<!-- agmod:end -->


This file orients coding agents to the tooling, workflows, and style rules for
this repository. It is derived from `docs/python_toolbox.md`,
`docs/code_style.md`, `docs/user-persona.md`, and
`agent_executor_instructions_v_1.md`, plus the current codebase conventions.

If a handoff or user request conflicts with this file, follow the handoff.

--------------------------------------------------------------------------------
Project snapshot

- Package name: `produm`
- Language: Python (requires >= 3.13)
- Layout: `src/project_dumper/`
- Entry point: `produm = project_dumper.cli:main`
- Tooling manager: `uv`

No Cursor rules or Copilot rules were found in:
- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

--------------------------------------------------------------------------------
Commands (build, lint, test)

Use `uv` for all environment and command execution. Avoid `pip`, `venv`, and
`conda` unless a handoff explicitly overrides this rule.

Build / packaging
- `uv build`
- `uv publish` (only when a release is intentionally requested)

Formatting
- `uv run black .`

Linting
- Minimal linting by default; do not add lint steps unless requested.
- If linting is required, prefer `ruff` with selected rules only.

Type checking
- `uv run mypy .`

Testing
- `uv run pytest`
- Tests are expected to live in `tests/` (none exist yet).

Run a single test (pytest)
- By file: `uv run pytest tests/test_example.py`
- By test node id: `uv run pytest tests/test_example.py::test_name`
- By keyword: `uv run pytest -k "keyword"`

Run the CLI locally
- `uv run produm`
- `uv run produm . -o dump.txt`

--------------------------------------------------------------------------------
Code style guidelines (authoritative)

These rules are enforced by `docs/code_style.md` and
`docs/python_toolbox.md`. Do not contradict them unless explicitly instructed.

Guiding principles
- Type hints first. Add explicit types to new or edited code.
- Avoid stringly-typed wiring (no `getattr`, `setattr`, or string-based glue
  in core logic).
- Keep functions small, testable, and readable over clever.
- Stable interfaces: do not break existing workflows without a clear request.

Imports
- Use `from __future__ import annotations` in Python modules.
- Order: standard library, third-party, then local imports.
- Group imports with blank lines between groups.
- Prefer `pathlib.Path` over string paths.

Formatting
- Black-compatible formatting everywhere.
- Do not hand-format to diverge from Black defaults.

Types
- Public functions and methods require full type hints.
- Avoid `Any` unless justified and localized.
- Favor explicit, named types over clever typing tricks.

Naming
- Functions: verb-based, explicit names.
- Helpers: prefix private helpers with `_`.
- Constants: `UPPER_SNAKE_CASE`.
- Include units in names when ambiguous (e.g., `time_s`, `freq_hz`).

Docstrings
- Required for: public APIs, domain/math functions, IO boundaries, non-obvious
  units/conventions/edge cases.
- Optional for: tiny internal helpers with self-evident behavior.
- Include: 1-2 line summary, parameters (with units), returns, key assumptions,
  failure modes when meaningful.
- Style: Google or NumPy; be consistent within a module.

Error handling
- Validate inputs early and raise explicit exceptions with actionable messages.
- CLI surfaces should convert internal exceptions into user-friendly messages.

Project structure
- Keep pure logic separate from IO and CLI.
- Keep CLI entry points thin: parse args -> call core -> format output.

Testing conventions
- Use `pytest`.
- Prefer deterministic tests (seed randomness).
- Cover core behavior, edge cases, and regression fixes.

Agent editing rules (from `docs/code_style.md`)
- Preserve public APIs unless explicitly instructed.
- Add docstrings only where required by policy.
- Keep changes small and localized.
- Add or update tests for any behavior change.
- Avoid refactors that change behavior just for style.

--------------------------------------------------------------------------------
Repository-specific notes

- The CLI currently uses `argparse` and prints a completion message.
- Default exclusions are defined in `src/project_dumper/constants.py`.
- Gitignore filtering is supported; do not change behavior without tests.

--------------------------------------------------------------------------------
When unsure

- Read `docs/code_style.md` and `docs/python_toolbox.md` first.
- Prefer explicit, small changes with tests when behavior changes.

--------------------------------------------------------------------------------
User persona (from `docs/user-persona.md`)

- Technical, pragmatic user; prefers simple, explicit Python code.
- Values clarity over elegance; explicit control flow over abstractions.
- Avoid frameworks and clever architectures unless requested.
- Strong preference for type hints, explicit attributes, and no reflection.
- Linux-centric, CLI/TUI oriented, minimal tooling.
- Output style: direct, pragmatic; show assumptions and tradeoffs; end concise.

--------------------------------------------------------------------------------
Agent executor instructions (from `agent_executor_instructions_v_1.md`)

- Treat the handoff document as the sole contract; chat history is not
  authoritative.
- Do not invent requirements or reinterpret scope.
- If anything is ambiguous or missing, stop and report the blocker.
- Implement all specified specs and follow constraints exactly.
- Testing is mandatory when executing: create missing tests if required and run
  all relevant tests without asking permission.
- Definition of Done requires all specified tests to pass and all commands to
  succeed; otherwise stop and report.
- Do not refactor or polish unless explicitly requested in the handoff.
