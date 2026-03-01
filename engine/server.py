from __future__ import annotations

import logging
import uuid

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from scalar_fastapi import get_scalar_api_reference

from engine import AkinatorEngine, GameState
from exceptions import (
    CantGoBackError,
    EngineError,
    InvalidAnswerError,
    InvalidLanguageError,
    NetworkError,
    SessionTimeoutError,
    StartupError,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Akin Engine",
    description="HTTP game server wrapping the Akinator API. Clients start a session, then drive it by posting answers.",
)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/scalar")


@app.get("/scalar", include_in_schema=False)
def scalar_ui() -> HTMLResponse:
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)

_sessions: dict[str, AkinatorEngine] = {}


# --------------------------------------------------------------------------- #
# Pydantic models                                                             #
# --------------------------------------------------------------------------- #

class GameStateOut(BaseModel):
    question: str = Field(description="Current question text")
    step: int = Field(description="Zero-based question index")
    progression: float = Field(description="Akinator's confidence (0–100)")
    win: bool = Field(description="Akinator has a guess ready")
    finished: bool = Field(description="Game is over")
    name_proposition: str | None = Field(description="Guessed character name")
    description_proposition: str | None = Field(description="Short description of the guess")

    @classmethod
    def from_state(cls, state: GameState) -> "GameStateOut":
        return cls(
            question=state.question,
            step=state.step,
            progression=state.progression,
            win=state.win,
            finished=state.finished,
            name_proposition=state.name_proposition,
            description_proposition=state.description_proposition,
        )


class StartGameRequest(BaseModel):
    language: str = Field("en", description="Two-letter language code (en ar zh de es fr he it ja ko nl pl pt ru tr id)")


class AnswerRequest(BaseModel):
    key: str = Field(description="Answer key: y (yes), n (no), ? (don't know), + (probably), - (probably not)")


class StartGameResponse(BaseModel):
    session_id: str = Field(description="Unique session ID - pass this in all later requests")
    state: GameStateOut


class StateResponse(BaseModel):
    state: GameStateOut


class ErrorDetail(BaseModel):
    error: str = Field(description="Error type name")
    message: str = Field(description="Human-readable error message")


class ErrorResponse(BaseModel):
    detail: ErrorDetail


# --------------------------------------------------------------------------- #
# Error mapping                                                               #
# --------------------------------------------------------------------------- #

_EXC_TO_STATUS: dict[type[EngineError], int] = {
    InvalidLanguageError: 422,
    StartupError: 503,
    InvalidAnswerError: 400,
    CantGoBackError: 409,
    SessionTimeoutError: 408,
    NetworkError: 502,
}


def _engine_exc_to_http(exc: EngineError) -> HTTPException:
    status = _EXC_TO_STATUS.get(type(exc), 500)
    logger.exception("Engine error (%s)", type(exc).__name__)
    return HTTPException(
        status_code=status,
        detail={"error": type(exc).__name__, "message": str(exc)},
    )


# --------------------------------------------------------------------------- #
# Session helpers                                                             #
# --------------------------------------------------------------------------- #

def _get_session(session_id: str) -> AkinatorEngine:
    engine = _sessions.get(session_id)
    if engine is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "SessionNotFound", "message": f"Session {session_id!r} not found"},
        )
    return engine


# --------------------------------------------------------------------------- #
# Reusable response docs                                                      #
# --------------------------------------------------------------------------- #

def _err(description: str) -> dict:
    return {"description": description, "model": ErrorResponse}

_R_SESSION = {404: _err("Session not found")}
_R_ENGINE  = {408: _err("Akinator session timed out"), 502: _err("Upstream Akinator API error")}


# --------------------------------------------------------------------------- #
# Routes                                                                      #
# --------------------------------------------------------------------------- #

@app.post("/games", response_model=StartGameResponse, status_code=201, responses={422: _err("Unsupported language code"), 503: _err("Failed to start a new game")})
def start_game(body: StartGameRequest) -> StartGameResponse:
    """Start a new game session. Returns a `session_id` to use in all later requests."""
    engine = AkinatorEngine()
    try:
        state = engine.start_game(body.language)
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    session_id = str(uuid.uuid4())
    _sessions[session_id] = engine
    return StartGameResponse(session_id=session_id, state=GameStateOut.from_state(state))


@app.post("/games/{session_id}/answer", response_model=StateResponse, responses={**_R_SESSION, **_R_ENGINE, 400: _err("Unknown answer key")})
def answer(session_id: str, body: AnswerRequest) -> StateResponse:
    """Submit an answer to the current question."""
    engine = _get_session(session_id)
    try:
        state = engine.answer(body.key)
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    return StateResponse(state=GameStateOut.from_state(state))


@app.post("/games/{session_id}/back", response_model=StateResponse, responses={**_R_SESSION, **_R_ENGINE, 409: _err("Already at the first question")})
def back(session_id: str) -> StateResponse:
    """Undo the last answer and return to the previous question."""
    engine = _get_session(session_id)
    try:
        state = engine.back()
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    return StateResponse(state=GameStateOut.from_state(state))


@app.post("/games/{session_id}/choose", response_model=StateResponse, responses={**_R_SESSION, **_R_ENGINE})
def choose(session_id: str) -> StateResponse:
    """Accept Akinator's guess - the game ends as a win."""
    engine = _get_session(session_id)
    try:
        state = engine.choose()
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    return StateResponse(state=GameStateOut.from_state(state))


@app.post("/games/{session_id}/exclude", response_model=StateResponse, responses={**_R_SESSION, **_R_ENGINE})
def exclude(session_id: str) -> StateResponse:
    """Reject Akinator's guess - the game continues with more questions."""
    engine = _get_session(session_id)
    try:
        state = engine.exclude()
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    return StateResponse(state=GameStateOut.from_state(state))


def start() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start()
