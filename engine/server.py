from __future__ import annotations

import logging
import uuid

import uvicorn

logger = logging.getLogger(__name__)
from exceptions import (
    CantGoBackError,
    EngineError,
    InvalidAnswerError,
    InvalidLanguageError,
    NetworkError,
    SessionTimeoutError,
    StartupError,
)
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from scalar_fastapi import get_scalar_api_reference

from engine import AkinatorEngine, GameState

app = FastAPI(title="Akin Engine")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/scalar")


@app.get("/scalar", include_in_schema=False)
def scalar_ui() -> HTMLResponse:
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)

_sessions: dict[str, AkinatorEngine] = {}


# --------------------------------------------------------------------------- #
# Pydantic models                                                              #
# --------------------------------------------------------------------------- #

class GameStateOut(BaseModel):
    question: str
    step: int
    progression: float
    win: bool
    finished: bool
    name_proposition: str | None
    description_proposition: str | None

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
    language: str = "en"


class AnswerRequest(BaseModel):
    key: str


class StartGameResponse(BaseModel):
    session_id: str
    state: GameStateOut


class StateResponse(BaseModel):
    state: GameStateOut


# --------------------------------------------------------------------------- #
# Error mapping                                                                #
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
# Session helpers                                                              #
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
# Routes                                                                       #
# --------------------------------------------------------------------------- #

@app.post("/games", response_model=StartGameResponse, status_code=201)
def start_game(body: StartGameRequest) -> StartGameResponse:
    engine = AkinatorEngine()
    try:
        state = engine.start_game(body.language)
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    session_id = str(uuid.uuid4())
    _sessions[session_id] = engine
    return StartGameResponse(session_id=session_id, state=GameStateOut.from_state(state))


@app.post("/games/{session_id}/answer", response_model=StateResponse)
def answer(session_id: str, body: AnswerRequest) -> StateResponse:
    engine = _get_session(session_id)
    try:
        state = engine.answer(body.key)
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    return StateResponse(state=GameStateOut.from_state(state))


@app.post("/games/{session_id}/back", response_model=StateResponse)
def back(session_id: str) -> StateResponse:
    engine = _get_session(session_id)
    try:
        state = engine.back()
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    return StateResponse(state=GameStateOut.from_state(state))


@app.post("/games/{session_id}/choose", response_model=StateResponse)
def choose(session_id: str) -> StateResponse:
    engine = _get_session(session_id)
    try:
        state = engine.choose()
    except EngineError as e:
        raise _engine_exc_to_http(e) from e
    return StateResponse(state=GameStateOut.from_state(state))


@app.post("/games/{session_id}/exclude", response_model=StateResponse)
def exclude(session_id: str) -> StateResponse:
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
