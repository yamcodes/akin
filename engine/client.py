from __future__ import annotations

import httpx

from .engine import GameState
from .exceptions import (
    CantGoBackError,
    EngineError,
    InvalidAnswerError,
    InvalidLanguageError,
    NetworkError,
    SessionTimeoutError,
    StartupError,
)

_ERROR_MAP: dict[str, type[EngineError]] = {
    "InvalidLanguageError": InvalidLanguageError,
    "StartupError": StartupError,
    "InvalidAnswerError": InvalidAnswerError,
    "CantGoBackError": CantGoBackError,
    "SessionTimeoutError": SessionTimeoutError,
    "NetworkError": NetworkError,
}


def _parse_error(response: httpx.Response) -> EngineError:
    try:
        detail = response.json().get("detail", {})
        error_type = detail.get("error", "")
        message = detail.get("message", response.text)
    except Exception:
        error_type = ""
        message = response.text
    exc_cls = _ERROR_MAP.get(error_type, NetworkError)
    return exc_cls(message)


def _state_from_dict(data: dict) -> GameState:
    s = data["state"]
    return GameState(
        question=s["question"],
        step=s["step"],
        progression=s["progression"],
        win=s["win"],
        finished=s["finished"],
        name_proposition=s.get("name_proposition"),
        description_proposition=s.get("description_proposition"),
    )


class EngineClient:
    """HTTP client with the same interface as AkinatorEngine."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self._session_id: str | None = None
        self._http = httpx.Client(base_url=base_url.rstrip("/"), timeout=30.0)

    def start_game(self, language: str = "en") -> GameState:
        try:
            resp = self._http.post("/games", json={"language": language})
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e
        if not resp.is_success:
            raise _parse_error(resp)
        data = resp.json()
        self._session_id = data["session_id"]
        return _state_from_dict(data)

    def _call(self, path: str, body: dict | None = None) -> GameState:
        if self._session_id is None:
            raise RuntimeError("engine not started")
        kwargs: dict = {"json": body} if body is not None else {}
        try:
            resp = self._http.post(f"/games/{self._session_id}/{path}", **kwargs)
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e
        if not resp.is_success:
            raise _parse_error(resp)
        return _state_from_dict(resp.json())

    def answer(self, key: str) -> GameState:
        return self._call("answer", {"key": key})

    def back(self) -> GameState:
        return self._call("back")

    def choose(self) -> GameState:
        return self._call("choose")

    def exclude(self) -> GameState:
        return self._call("exclude")
