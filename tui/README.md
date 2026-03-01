# akin-tui

Terminal UI for [akin](../README.md), built with [Textual](https://textual.textualize.io/).
Requires the engine server to be running — see [engine/README.md](../engine/README.md).

## Running

```bash
uv sync
uv run python main.py [language] [--debug] [--engine-url URL]
```

**Examples**

```bash
uv run python main.py              # English, engine at localhost:8000
uv run python main.py es           # Spanish
uv run python main.py en --debug   # show step + progression % after each answer
uv run python main.py en --engine-url http://my-server:8000
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `language` | `en` | Two-letter language code (`en es pt fr de` …) |
| `--debug` | off | Show step number and progression % in the status bar |
| `--engine-url` | `$ENGINE_URL` or `http://localhost:8000` | Engine server base URL |

`--engine-url` falls back to the `ENGINE_URL` environment variable, then `http://localhost:8000`.

## Key bindings

| Key | Action |
|-----|--------|
| `y` | Yes |
| `n` | No |
| `?` | I don't know |
| `+` | Probably |
| `-` | Probably not |
| `b` | Back (undo last answer) |
| `q` | Quit |

When Akinator makes a guess, `y` accepts it (you win) and `n` rejects it (game continues).

## Distribution

The `[project.scripts]` entry in `pyproject.toml` exposes an `akin` command for Homebrew:

```bash
akin [language] [--debug] [--engine-url URL]
```

Local dev uses `uv run python main.py` directly.
