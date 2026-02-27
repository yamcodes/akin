# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Script

```bash
python akinator.py <name> <age> <gender> [language]
# Example:
python akinator.py Alice 25 F en
```

- `gender`: `M` or `F`
- `language`: two-letter code (e.g., `en`, `es`, `pt`); defaults to `en`
- Age must be greater than 8

## Dependencies

This is a **Python 2** script. It requires:
- `twisted` (for async HTTP via `twisted.internet` and `twisted.web`)
- `talkinator` (provides `BeautifulSoup` via `talkinator.BeautifulSoup`)

There is no `requirements.txt` or package manifest.

## Architecture

Single-file script (`akinator.py`) with two components:

- **`AkinatorChat`** — stateful iterator that manages a game session with akinator.com. It tracks session state (`partie`, `signature`, `session`, `count`) and builds URLs for the akinator API endpoints (`new_session.php` on first call, `repondre_propose.php` on subsequent calls). `parse_html` uses BeautifulSoup to extract questions/answers from the HTML response.

- **`interactive()`** — a `@defer.inlineCallbacks` coroutine that drives the game loop: iterates over the `AkinatorChat` object, yields each deferred HTTP request, prints questions, reads answers from stdin via `raw_input`, and stops when a result or error is returned.

The script targets the old akinator.com API (circa 2012) and may no longer work against the live site.
