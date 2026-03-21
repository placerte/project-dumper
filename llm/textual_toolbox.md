---
id: BLK-TOOLBOX-TEXTUAL-V1
name: Textual Toolbox
type: toolbox
scope: app-dev
version: 1.0
status: deprecated
revised: 2026-03-20
summary: Defaults for Textual UI development and testing.
---

# Textual Toolbox (Authoritative)

This document defines the default approach for **Textual**-based TUIs, with emphasis on how an execution agent should **test and visually validate** UI behavior.

Unless a handoff overrides it, these are the defaults for any Textual project.

---

## Scope

Applies to:
- Textual app development
- agent-driven UI testing
- review loops where UI behavior must be validated deterministically

---

## Dependencies

- UI framework: **Textual**

Recommended (when UI testing is required):
- Textual’s **Pilot**-based testing utilities

---

## UI Testing Priority Order (Hard Rule)

When an agent needs to “see and test” the UI, it must use this priority order:

1) **Textual Pilot** toolset (primary)
   - drive the app deterministically
   - assert screen state / widgets
   - simulate user interactions

2) **Snapshots** + visual inspection (secondary)
   - use snapshots to capture UI states
   - compare layout regressions and density issues

3) **asciinema `.cast` review** (last resort)
   - only when Pilot/snapshots cannot represent the issue
   - used for human/agent playback review of flows

Do not jump to `.cast` unless the first two paths are insufficient.

---

## Testing Principles

- Prefer **deterministic** tests over manual observation.
- A “graceful failure” that shows an error message in the UI is still a testable outcome.
- Tests should assert:
  - screen transitions
  - error banners/messages
  - presence/absence of key widgets
  - key bindings that drive flows

---

## Agent Execution Expectations

If a handoff asks to validate a Textual UI:
- write Pilot tests where feasible
- run tests via the project’s standard entry point (typically `uv run pytest`)
- include at least one test that covers:
  - the main happy path
  - one representative failure path (bad input, missing file, etc.)

If the agent cannot produce a deterministic test for a UI behavior:
- capture snapshots
- explain why Pilot was insufficient
- only then use `.cast` as supporting evidence

---

## Non-goals

- This document does not define a UI design system.
- It does not mandate a specific app architecture.
- It does not replace a handoff contract.

---

## Status

Authoritative v1
