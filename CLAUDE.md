# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

Phase 2 requires two processes (engine server + TUI):

```bash
# Terminal 1: start the engine HTTP server
poetry run python engine/server.py

# Terminal 2: start the TUI
poetry run python tui/main.py [language] [--debug] [--engine-url URL]
# Examples:
poetry run python tui/main.py
poetry run python tui/main.py es
poetry run python tui/main.py en --debug
poetry run python tui/main.py en --engine-url http://localhost:8000
```

- `language`: two-letter code (e.g., `en`, `es`, `pt`); defaults to `en`
- `--debug`: shows progression % and step after each answer
- `--engine-url`: engine server URL; defaults to `http://localhost:8000`

The PoC (terminal, no TUI) is still available at `poc/main.py`.

## Dependencies

Managed via **Poetry**:

```bash
poetry install
```

Dependencies: `akinator`, `readchar`, `cloudscraper`, `textual`, `fastapi`, `uvicorn`, `httpx`.

## Architecture

```
engine/          # Game logic + HTTP server/client
  exceptions.py  # EngineError hierarchy
  engine.py      # AkinatorEngine + GameState dataclass
  server.py      # FastAPI HTTP server (uvicorn)
  client.py      # EngineClient — same interface as AkinatorEngine, talks HTTP
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

**`EngineClient`** exposes the same interface as `AkinatorEngine` but communicates over HTTP. It manages a `session_id` obtained from `POST /games` and passes it in all subsequent requests.

**Key bindings**: `y n ? + -` (answers), `b` (back), `q` (quit).

## Notes

- The old 2012 akinator.com API is dead. The `akinator` (Ombucha) library uses `cloudscraper` to bypass Cloudflare.
- `tui/app.py` uses `on_key` directly (not BINDINGS) so that `?`, `+`, `-` are captured correctly.
