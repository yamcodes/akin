# akin

A monorepo for an Akinator CLI experience.

## Architecture

The project is built in phases, each adding a layer while keeping the previous one intact as reference.

**PoC** — single file, no separation of concerns:
```
poc/main.py  (everything: UI, game logic, HTTP)
```

**Phase 1** — TUI talks directly to the engine via Python import:
```
tui/  ──import──►  engine/
```

**Phase 2** — TUI talks to a server, server owns session state and talks to the engine:
```
tui/  ──http──►  server/  ──import──►  engine/
```

The engine only ever wraps the akinator library — it has no awareness of who is calling it.

## Structure

| Directory | Description                                        |
|-----------|----------------------------------------------------|
| `poc/`    | Original single-file PoC — 109 lines, plain Python |
| `engine/` | Python wrapper around the akinator library         |
| `tui/`    | Frontend (Textual)                                 |
| `server/` | Spring Boot server, hypermedia, session state      |

## Acknlowedgements

- Thanks [fiorix](https://gist.github.com/fiorix) for original gist: https://gist.github.com/fiorix/3152830
- Thanks [Omkaar](https://github.com/Ombucha) for the [`akinator`](https://github.com/Ombucha/akinator.py) library, which powers the game session and Cloudflare bypass
