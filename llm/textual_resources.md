---
id: BLK-TOOLBOX-TEXTUAL-RESOURCES-V1
name: Textual Friendly Reference
type: toolbox
scope: app-dev
version: 1.0
status: deprecated
revised: 2026-03-20
summary: Practical guidance for building Textual apps.
---

## Textual Friendly Reference

Practical, friendly guidance for building Textual apps. This complements
`llm/textual_toolbox.md` (testing policy) with day-to-day development tips.

Primary docs: https://textual.textualize.io/

---

## Quick App Skeleton

```python
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static


class MyApp(App[None]):
    TITLE = "My App"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Hello, Textual!")
        yield Footer()


if __name__ == "__main__":
    MyApp().run()
```

---

## Compose, Widgets, and Containers

Use `compose()` to declare your UI. Prefer containers for layout:

```python
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, Tree

def compose(self) -> ComposeResult:
    with Horizontal():
        yield Tree("Sources")
        with VerticalScroll():
            yield Label("Details")
```

Tips:
- `VerticalScroll` and `HorizontalScroll` are ideal for large content.
- Prefer `query_one()` for well-known widgets (`#id`), `query()` for sets.

---

## Styles (TCSS)

Textual uses CSS-like styling. A minimal TCSS block:

```python
DEFAULT_CSS = """
Screen {
    background: $background;
}
#sidebar {
    width: 30;
    border: round $accent;
}
"""
```

Notes:
- Use theme variables like `$accent`, `$surface`, `$text-muted`.
- Prefer `content-align`, `padding`, and `margin` to control spacing.

---

## Reactivity and State

Textual provides reactive state updates:

```python
from textual.reactive import reactive

class MyWidget(Static):
    count: int = reactive(0)

    def watch_count(self, value: int) -> None:
        self.update(f"Count: {value}")
```

---

## Actions and Key Bindings

```python
from textual.binding import Binding

class MyApp(App[None]):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def action_refresh(self) -> None:
        self.refresh()
```

---

## Themes and Colors

Themes are registered per app:

```python
from textual.theme import Theme

MY_THEME = Theme(
    name="my-theme",
    primary="#88C0D0",
    background="#2E3440",
    foreground="#D8DEE9",
    accent="#B48EAD",
    dark=True,
)

def on_mount(self) -> None:
    self.register_theme(MY_THEME)
    self.theme = "my-theme"
```

Theme tokens can be used in TCSS: `$primary`, `$accent`, `$surface`, `$text`.

---

## Testing (Pilot First)

Use `run_test()` with Pilot for deterministic UI tests:

```python
async with app.run_test() as pilot:
    await pilot.press("q")
```

Then use `export_screenshot()` to capture snapshots if needed.

---

## Common Pitfalls

- If styles do not apply, confirm the widget has an `id` or class in TCSS.
- For theme variables in markup, use `[$accent]text[/]` (note the `$`).
- If a widget does not update, call `.refresh()` or update reactive state.

---

## Useful Links

- Getting started: https://textual.textualize.io/getting_started/
- Guide (App Basics, Layout, Styles, Actions, Reactivity):
  https://textual.textualize.io/guide/
- Widgets gallery: https://textual.textualize.io/widget_gallery/
- Themes: https://textual.textualize.io/guide/design/
- Testing: https://textual.textualize.io/guide/testing/
