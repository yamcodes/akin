# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

```bash
poetry run python tui/main.py [language] [--debug]
# Examples:
poetry run python tui/main.py
poetry run python tui/main.py es
poetry run python tui/main.py en --debug
```

- `language`: two-letter code (e.g., `en`, `es`, `pt`); defaults to `en`
- `--debug`: shows progression % and step after each answer

The PoC (terminal, no TUI) is still available at `poc/main.py`.

## Dependencies

Managed via **Poetry**:

```bash
poetry install
```

Dependencies: `akinator`, `readchar`, `cloudscraper`, `textual`.

## Architecture

```
engine/          # Pure game logic — no UI
  exceptions.py  # EngineError hierarchy
  engine.py      # AkinatorEngine + GameState dataclass
  __init__.py

tui/             # Textual TUI frontend
  app.py         # AkinatorApp (App) — worker pattern, state machine
  widgets.py     # QuestionHistory, CurrentQuestion, WinProposal, StatusBar
  app.tcss       # Textual CSS
  main.py        # Entry point: argparse → AkinatorApp().run()
  __init__.py

poc/
  main.py        # Original single-file PoC (readchar, no Textual)
```

**`AkinatorEngine`** wraps the sync `akinator.client.Akinator`. All methods return a frozen `GameState` dataclass. Workers run engine calls off the main thread.

**Key bindings**: `y n ? + -` (answers), `b` (back), `q` (quit).

## Notes

- The old 2012 akinator.com API is dead. The `akinator` (Ombucha) library uses `cloudscraper` to bypass Cloudflare.
- `tui/app.py` uses `on_key` directly (not BINDINGS) so that `?`, `+`, `-` are captured correctly.
