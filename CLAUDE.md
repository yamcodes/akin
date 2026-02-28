# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Script

```bash
python main.py [language]
# Examples:
python main.py
python main.py es
python main.py en --debug
```

- `language`: two-letter code (e.g., `en`, `es`, `pt`); defaults to `en`
- `--debug`: prints progression % and step after each answer

## Dependencies

This is a **Python 3** script. Dependencies are managed via a `.venv` virtualenv:

```bash
source .venv/bin/activate
pip install akinator readchar cloudscraper
```

Or use the alias defined in `~/.bash_aliases`:

```bash
akinator [language] [--debug]
```

## Architecture

Single-file script (`main.py`) with two components:

- **`read_key(prompt)`** — prints a prompt, reads a single keypress via `readchar`, handles Ctrl+C by raising `KeyboardInterrupt`.

- **`interactive(language, debug)`** — drives the game loop using the `akinator` (Ombucha) library. Starts a session, loops until `aki.finished`, handles win proposals (`aki.win`) by asking for confirmation, maps shorthand keys (`?`, `+`, `-`) to the library's answer strings, and prints debug info if `--debug` is passed.

## Notes

- The old 2012 akinator.com API is dead. The `akinator` (Ombucha) library uses `cloudscraper` to bypass Cloudflare.
- The script was previously named `akinator.py` but renamed to `main.py` to avoid a Python import name conflict with the `akinator` package.
