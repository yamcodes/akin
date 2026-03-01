# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

Phase 2 requires two processes (engine server + TUI):

```bash
# One-time setup
(cd engine && uv sync)
(cd tui && uv sync)

# Terminal 1: start the engine HTTP server
cd engine && uv run python server.py

# Terminal 2: start the TUI
cd tui && uv run python main.py [language] [--debug] [--engine-url URL]
# Examples:
cd tui && uv run python main.py
cd tui && uv run python main.py es
cd tui && uv run python main.py en --debug
cd tui && uv run python main.py en --engine-url http://localhost:8000
```

- `language`: two-letter code (e.g., `en`, `es`, `pt`); defaults to `en`
- `--debug`: shows progression % and step after each answer
- `--engine-url`: engine server URL; defaults to `ENGINE_URL` env var, then `http://localhost:8000`

The PoC (terminal, no TUI) is still available at https://github.com/yamcodes/akin/blob/poc/main.py.

## Docker

```bash
# Start the engine server via Docker
docker compose up
```

TUI runs natively, pointing to the Dockerized engine (`http://localhost:8000`).

## Dependencies

Managed via **uv** (per-service):

```bash
(cd engine && uv sync)   # installs engine deps + generates engine/uv.lock
(cd tui && uv sync)      # installs tui deps + generates tui/uv.lock
```

Both `engine/uv.lock` and `tui/uv.lock` are committed for reproducible installations.

## Architecture

```
engine/          # Game logic + HTTP server (standalone uv project)
  exceptions.py  # EngineError hierarchy
  engine.py      # AkinatorEngine + GameState dataclass
  server.py      # FastAPI HTTP server (uvicorn)
  pyproject.toml # uv project: akinator, cloudscraper, fastapi, uvicorn[standard]
  Dockerfile     # Python slim + uv, exposes :8000

tui/             # Textual TUI frontend (standalone uv project)
  app.py         # AkinatorApp (App) - worker pattern, state machine
  widgets.py     # QuestionHistory, CurrentQuestion, WinProposal, StatusBar
  client.py      # GameState + exceptions + EngineClient (HTTP client)
  app.tcss       # Textual CSS
  main.py        # Entry point: argparse → AkinatorApp().run()
  pyproject.toml # uv project: textual, httpx, readchar

docker-compose.yml  # engine service; web/ joins in Phase 3
```

**`AkinatorEngine`** wraps the sync `akinator.client.Akinator`. All methods return a frozen `GameState` dataclass. Workers run engine calls off the main thread.

**`EngineClient`** (in `tui/client.py`) exposes the same interface as `AkinatorEngine` but communicates over HTTP. It manages a `session_id` obtained from `POST /games` and passes it in all later requests.

**Key bindings**: `y n ? + -` (answers), `b` (back), `q` (quit).

## Import strategy

Each service runs from its own directory (`cd engine && uv run python server.py`).
Python's `sys.path` includes `.` (cwd), so imports are absolute within the service:

- `engine/server.py`: `from engine import ...` finds `engine/engine.py`; `from exceptions import ...` finds `engine/exceptions.py`
- `tui/app.py`: `from client import ...` finds `tui/client.py`; `from widgets import ...` finds `tui/widgets.py`

## Notes

- The old 2012 akinator.com API is dead. The `akinator` (Ombucha) library uses `cloudscraper` to bypass Cloudflare.
