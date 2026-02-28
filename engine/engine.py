from __future__ import annotations

from dataclasses import dataclass

from akinator.client import Akinator
from akinator import exceptions as _aki_exc

from .exceptions import (
    CantGoBackError,
    InvalidAnswerError,
    InvalidLanguageError,
    NetworkError,
    SessionTimeoutError,
    StartupError,
)


@dataclass(frozen=True)
class GameState:
    question: str
    step: int
    progression: float
    win: bool
    finished: bool
    name_proposition: str | None
    description_proposition: str | None


LANGUAGE_MAP = {
    "en": "english", "ar": "arabic",  "zh": "chinese",
    "de": "german",  "es": "spanish", "fr": "french",
    "he": "hebrew",  "it": "italian", "ja": "japanese",
    "ko": "korean",  "nl": "dutch",   "pl": "polish",
    "pt": "portuguese", "ru": "russian", "tr": "turkish",
    "id": "indonesian",
}

ANSWER_ALIASES = {
    "y": "yes",
    "n": "no",
    "?": "idk",
    "+": "probably",
    "-": "probably not",
}


class AkinatorEngine:
    def __init__(self) -> None:
        self._aki: Akinator | None = None

    def _snapshot(self) -> GameState:
        aki = self._aki
        if aki is None:
            raise RuntimeError("engine not started")
        return GameState(
            question=aki.question,
            step=aki.step,
            progression=aki.progression,
            win=aki.win,
            finished=aki.finished,
            name_proposition=getattr(aki, "name_proposition", None),
            description_proposition=getattr(aki, "description_proposition", None),
        )

    def start_game(self, language: str = "en") -> GameState:
        aki = Akinator()
        language = LANGUAGE_MAP.get(language.lower(), language.lower())
        try:
            aki.start_game(language=language)
        except _aki_exc.InvalidLanguageError as e:
            raise InvalidLanguageError(str(e)) from e
        except Exception as e:
            raise StartupError(str(e)) from e
        self._aki = aki
        return self._snapshot()

    def answer(self, key: str) -> GameState:
        aki = self._aki
        if aki is None:
            raise RuntimeError("engine not started")
        answer_str = ANSWER_ALIASES.get(key, key)
        try:
            aki.answer(answer_str)
        except _aki_exc.InvalidChoiceError as e:
            raise InvalidAnswerError(str(e)) from e
        except _aki_exc.TimeoutError as e:
            raise SessionTimeoutError(str(e)) from e
        except Exception as e:
            raise NetworkError(str(e)) from e
        return self._snapshot()

    def back(self) -> GameState:
        aki = self._aki
        if aki is None:
            raise RuntimeError("engine not started")
        try:
            aki.back()
        except _aki_exc.CantGoBackAnyFurther as e:
            raise CantGoBackError(str(e)) from e
        except _aki_exc.TimeoutError as e:
            raise SessionTimeoutError(str(e)) from e
        except Exception as e:
            raise NetworkError(str(e)) from e
        return self._snapshot()

    def choose(self) -> GameState:
        aki = self._aki
        if aki is None:
            raise RuntimeError("engine not started")
        try:
            aki.choose()
        except _aki_exc.TimeoutError as e:
            raise SessionTimeoutError(str(e)) from e
        except Exception as e:
            raise NetworkError(str(e)) from e
        return self._snapshot()

    def exclude(self) -> GameState:
        aki = self._aki
        if aki is None:
            raise RuntimeError("engine not started")
        try:
            aki.exclude()
        except _aki_exc.TimeoutError as e:
            raise SessionTimeoutError(str(e)) from e
        except Exception as e:
            raise NetworkError(str(e)) from e
        return self._snapshot()
