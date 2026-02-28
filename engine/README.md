# akin-engine

HTTP game server wrapping the [akinator.py](https://github.com/Ombucha/akinator.py) library.
Clients start a game session, then drive it by posting answers.

## Running

### Locally

```bash
uv sync
uv run python server.py
# → uvicorn listening on http://0.0.0.0:8000
```

### Docker

```bash
# from the repo root
docker compose up
```

The image is built from `engine/Dockerfile`.
Port `8000` is exposed and forwarded to the host.

## API

All responses include a `state` object (see [Game state](#game-state)).
On error, responses include `{"detail": {"error": "<ErrorType>", "message": "<text>"}}`.

### Start a game

```
POST /games
```

**Body**

```json
{ "language": "en" }
```

Supported language codes: `en ar zh de es fr he it ja ko nl pl pt ru tr id`

**Response** `201`

```json
{
  "session_id": "3fa85f64-...",
  "state": { ... }
}
```

---

### Answer a question

```
POST /games/{session_id}/answer
```

**Body**

```json
{ "key": "y" }
```

| Key | Meaning |
|-----|---------|
| `y` | Yes |
| `n` | No |
| `?` | I don't know |
| `+` | Probably |
| `-` | Probably not |

**Response** `200` — updated `state`

---

### Go back

```
POST /games/{session_id}/back
```

No body. Returns updated `state`.
Returns `409` if already at the first question.

---

### Accept a proposition (you got it right)

```
POST /games/{session_id}/choose
```

No body. Finalises the game as a win (`finished=true, win=true`).

---

### Reject a proposition (keep going)

```
POST /games/{session_id}/exclude
```

No body. Tells Akinator its guess was wrong; resumes questioning.

---

## Game state

Every response wraps the current game state:

```json
{
  "state": {
    "question": "Is your character real?",
    "step": 4,
    "progression": 38.5,
    "win": false,
    "finished": false,
    "name_proposition": null,
    "description_proposition": null
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | Current question text |
| `step` | int | Zero-based question index |
| `progression` | float | Akinator's confidence 0–100 |
| `win` | bool | Akinator has a guess |
| `finished` | bool | Game is over |
| `name_proposition` | string \| null | Guessed character name |
| `description_proposition` | string \| null | Short description of the guess |

**State transitions**

- `win=true, finished=false` — Akinator is guessing; call `/choose` or `/exclude`
- `win=true, finished=true` — Akinator won; game over
- `win=false, finished=true` — Akinator gave up; game over

## Error codes

| Status | Error type | Cause |
|--------|------------|-------|
| 400 | `InvalidAnswerError` | Unknown answer key |
| 404 | `SessionNotFound` | Bad or expired session ID |
| 408 | `SessionTimeoutError` | Akinator session timed out |
| 409 | `CantGoBackError` | Already at question 0 |
| 422 | `InvalidLanguageError` | Unsupported language code |
| 502 | `NetworkError` | Upstream Akinator API error |
| 503 | `StartupError` | Failed to start a new game |
