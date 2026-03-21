---
id: BLK-TOOLBOX-PROGRESS-TRACKER-V1
name: Progress Tracker
type: toolbox
scope: core
version: 1.0
status: deprecated
revised: 2026-03-20
summary: Progress tracking system for requirements and evidence.
---

# progress_tracker.md

## Purpose

This file defines the **progress tracking system used by agents when implementing requirements** from handoffs, specifications, or other structured request formats.

The goal is to maintain **clear traceability between requirements, implementation, tests, and completion evidence**.

Progress tracking uses two artifacts:

```text
docs/
├─ progress_tracker.md   # instructions for agents
└─ progress_tracker.csv  # actual tracker data
```

Agents must update the CSV file while following the conventions defined in this document.

The tracker is an important coordination artifact, but it is **not guaranteed to be perfectly up to date**. Agents must assume drift is possible and cross-check the tracker against the handoff, the codebase, tests, and recent changes when needed.

---

# 1. Core Principle: Traceability

Every requirement should be traceable across four locations:

1. **Specification / Handoff**
2. **Tracker row**
3. **Code implementation**
4. **Evidence of completion**

This creates a bidirectional reference system:

```text
Spec → Tracker → Code → Evidence
Code → Requirement ID
```

Agents should maintain this linkage whenever implementing features, while recognizing that real projects may contain partial, outdated, or missing tracker information.

---

# 2. Requirement IDs

Requirements are identified using structured IDs such as:

```text
S-YYYYMMDD-x     Specification
I-YYYYMMDD-x     Implementation
T-YYYYMMDD-x     Test
DoD-YYYYMMDD-x   Definition of Done
```

Agents must preserve these identifiers exactly.

IDs are used:

- in tracker rows
- in code comments
- in tests
- in documentation

---

# 3. Code Cross-Tagging

When implementing a requirement, agents must place **requirement tags in code comments** at meaningful locations.

Preferred format:

```python
# [S-260310-1.1]
# [I-260310-1.1]
```

Example:

```python
def render_curve(curve):
    # [S-260310-1.1] display selected curve
    # [I-260310-1.1] plotting implementation
    fig = plot_curve(curve)
    return fig
```

Tags should appear at logical implementation anchors, such as:

- public functions
- UI handlers
- data processing functions
- validation logic
- persistence operations
- tests

Avoid tagging trivial lines.

One location may reference multiple requirement IDs.

Tags must remain easy to search using grep.

---

# 4. Progress Tracker CSV

`progress_tracker.csv` stores the live status of all tracked items.

Recommended schema:

```text
item_id,item_type,title,status,module,symbol,impl_locations,test_locations,code_tags,evidence_type,evidence_ref,notes
```

Example row:

```text
S-260310-1.1,Spec,Render selected curve,Implemented,curve_viewer.py,UnitCurveViewer.render,curve_viewer.py::UnitCurveViewer.render,tests/test_curve_viewer.py::test_render,[S-260310-1.1],manual,curve visible after selection,
```

Key fields:

| Column | Purpose |
|---|---|
| item_id | requirement identifier |
| item_type | Spec / Impl / Test / DoD |
| status | implementation status |
| module | primary module involved |
| symbol | main class/function |
| impl_locations | file::symbol references |
| test_locations | test implementations |
| code_tags | requirement tags inserted in code |
| evidence_type | type of completion evidence |
| evidence_ref | proof of completion |
| notes | extra context |

Multiple locations may be separated using `;`.

---

# 5. Status Values

Agents must use consistent status values.

Allowed statuses:

```text
Not Started
In Progress
Implemented
Verified
Blocked
Obsolete
```

`Obsolete` is used when a tracked item is no longer the intended path forward, even if it remains useful as historical context.

Rules:

- **Implemented** means code exists, tags exist, and the tracker row is updated.
- **Verified** means implementation exists and at least one evidence entry is recorded.

Agents must not mark an item as **Verified** without evidence.

Agents may mark an item as **Obsolete** when:

- the implementation direction changed
- the requirement was superseded
- the tracker preserved an abandoned path for historical reasons
- the row no longer reflects the current intended solution

When marking an item **Obsolete**, agents should record the reason in `notes`.

---

# 6. Completion Evidence

Every verified item must include a small proof field in the tracker.

Allowed evidence types:

```text
test
manual
snapshot
log
review
```

Examples:

```text
test,tests/test_curve_viewer.py::test_selected_curve_renders
manual,curve visible after selecting one row in notebook
snapshot,artifacts/unit_curve_viewer_selected_curve.png
log,traceability_check passed for S-260310-1.1
review,confirmed during code review
```

This rule helps prevent agents from claiming completion without proof.

---

# 7. Updating the Tracker

Whenever a requirement is implemented, agents must:

1. Insert requirement tags in code.
2. Update the corresponding row in `progress_tracker.csv`.
3. Record implementation locations.
4. Record test locations if applicable.
5. Update the status.
6. Add completion evidence when the item is verified.

A requirement should not be marked **Implemented** unless at least one code location is recorded.

A requirement should not be marked **Verified** unless at least one evidence entry is recorded.

If tracker drift is discovered, agents should prefer correcting the tracker rather than forcing the codebase to match stale tracker data.

---

# 8. Editing Rules for Agents

When working on a project using this tracker:

1. Inspect `progress_tracker.csv` first.
2. Cross-check it against the handoff, specs, codebase, tests, and any recent changes when relevant.
3. Identify items that are **Not Started** or **In Progress**.
4. Implement requirements.
5. Add cross-tags in code.
6. Update the tracker row.
7. Record evidence before marking an item **Verified**.
8. If the tracker appears stale or contradictory, correct it and explain the reason in `notes`.

Agents should treat the tracker as a **working progress ledger**, not as the only source of truth.

---

# 9. Drift and Reality Checks

Tracker drift can happen for many reasons, including:

- the tracker was introduced after work had already started
- an earlier agent failed to maintain the tracker
- a third party changed code without updating the tracker
- implementation strategy changed after the tracker row was created

Because of this, agents must not assume that tracker state is always correct.

When contradictions appear, agents should:

1. inspect the code and tests
2. inspect the handoff or source spec
3. determine the most likely current reality
4. update the tracker to reflect that reality
5. preserve historical context when useful

The tracker should follow the project reality, not the other way around.

---

# Summary

The progress tracker system provides:

- requirement traceability
- implementation auditability
- agent coordination
- structured project progress tracking
- explicit completion evidence
- controlled handling of tracker drift and obsolete rows

Tracker = **project progress ledger**  
Code tags = **implementation anchors**  
Evidence = **proof of completion**

Together they provide reliable traceability between **specification, implementation, tests, and verification**, while still allowing the tracker to adapt to real project evolution.
