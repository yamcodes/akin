from __future__ import annotations

import sys
import os

from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Header, Footer
from textual.worker import Worker, WorkerState

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine import (
    AkinatorEngine,
    GameState,
    CantGoBackError,
    InvalidAnswerError,
    InvalidLanguageError,
    NetworkError,
    SessionTimeoutError,
    StartupError,
)
from tui.widgets import CurrentQuestion, QuestionHistory, StatusBar, WinProposal

ANSWER_KEYS = {"y", "n", "?", "+", "-"}


class AkinatorApp(App):
    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, language: str = "en", debug: bool = False) -> None:
        super().__init__()
        self._language = language
        self._debug = debug
        self._engine = AkinatorEngine()
        self._loading = False
        self._game_over = False
        self._awaiting_win = False
        # Track current question/step for history recording on keypress
        self._cur_question: str = ""
        self._cur_step: int = 0
        self._cur_name: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield QuestionHistory(id="history")
        yield CurrentQuestion("Starting...", id="current")
        yield WinProposal(id="win_proposal")
        yield StatusBar("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self._do_start_game()

    # ------------------------------------------------------------------ #
    # Key handling                                                         #
    # ------------------------------------------------------------------ #

    def on_key(self, event: Key) -> None:
        if self._loading or self._game_over:
            event.stop()
            return

        key = event.character or event.key

        if self._awaiting_win:
            if key == "y":
                event.stop()
                self._win_accept()
            elif key == "n":
                event.stop()
                self._win_reject()
            # all other keys ignored while awaiting win response
            return

        if key in ANSWER_KEYS:
            event.stop()
            self._do_answer(key)
        elif key == "b":
            event.stop()
            self._do_back()
        # q is handled by the BINDINGS action

    # ------------------------------------------------------------------ #
    # Engine workers                                                       #
    # ------------------------------------------------------------------ #

    def _do_start_game(self) -> None:
        self._set_loading(True)
        self.run_worker(lambda: self._engine.start_game(self._language), thread=True, name="engine")

    def _do_answer(self, key: str) -> None:
        history = self.query_one("#history", QuestionHistory)
        history.append_qa(self._cur_step + 1, self._cur_question, key)
        self._set_loading(True)
        self.run_worker(lambda: self._engine.answer(key), thread=True, name="engine")

    def _do_back(self) -> None:
        self._set_loading(True)
        self.run_worker(self._engine.back, thread=True, name="engine")

    def _win_accept(self) -> None:
        history = self.query_one("#history", QuestionHistory)
        history.append_win(self._cur_name, "Correct!")
        self._set_loading(True)
        self.run_worker(self._engine.choose, thread=True, name="engine")

    def _win_reject(self) -> None:
        history = self.query_one("#history", QuestionHistory)
        history.append_win(self._cur_name, "Nope, keep going...")
        self._set_loading(True)
        self.run_worker(self._engine.exclude, thread=True, name="engine")

    # ------------------------------------------------------------------ #
    # Worker result / error                                               #
    # ------------------------------------------------------------------ #

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "engine":
            return
        if event.state == WorkerState.SUCCESS:
            self._set_loading(False)
            self._apply_state(event.worker.result)
        elif event.state == WorkerState.ERROR:
            self._set_loading(False)
            self._handle_error(event.worker.error)

    # ------------------------------------------------------------------ #
    # State machine                                                        #
    # ------------------------------------------------------------------ #

    def _apply_state(self, state: GameState) -> None:
        current = self.query_one("#current", CurrentQuestion)
        win_proposal = self.query_one("#win_proposal", WinProposal)

        if self._debug:
            self.query_one("#status", StatusBar).flash(
                f"step={state.step}  progression={state.progression:.1f}%",
                duration=5.0,
            )

        if state.finished and state.win:
            win_proposal.hide()
            current.show_result(
                f"[bold green]I got it![/bold green] [bold]{state.name_proposition}[/bold]!\n"
                f"[dim]{state.description_proposition}[/dim]"
            )
            self._game_over = True
            self._awaiting_win = False
            return

        if state.finished and not state.win:
            win_proposal.hide()
            current.show_result("[bold red]I give up![/bold red] Good game!")
            self._game_over = True
            self._awaiting_win = False
            return

        if state.win and not state.finished:
            self._awaiting_win = True
            self._cur_name = state.name_proposition or ""
            win_proposal.show(
                state.name_proposition or "",
                state.description_proposition or "",
            )
            current.show_win_prompt(
                state.name_proposition or "",
                state.description_proposition or "",
            )
            return

        # Normal question
        self._awaiting_win = False
        win_proposal.hide()
        self._cur_question = state.question
        self._cur_step = state.step
        current.show_question(state.step, state.question)

    # ------------------------------------------------------------------ #
    # Error handling                                                       #
    # ------------------------------------------------------------------ #

    def _handle_error(self, exc: BaseException | None) -> None:
        status = self.query_one("#status", StatusBar)
        current = self.query_one("#current", CurrentQuestion)

        if isinstance(exc, InvalidLanguageError):
            status.flash(f"Invalid language '{self._language}', retrying with English...")
            self._language = "en"
            self._do_start_game()
        elif isinstance(exc, CantGoBackError):
            status.flash("Can't go back any further")
            # Re-display current question
            current.show_question(self._cur_step, self._cur_question)
        elif isinstance(exc, InvalidAnswerError):
            status.flash("Invalid answer")
            current.show_question(self._cur_step, self._cur_question)
        elif isinstance(exc, SessionTimeoutError):
            status.flash("Session timed out. Please restart.")
            self._game_over = True
        elif isinstance(exc, (NetworkError, StartupError)):
            status.flash(f"Error: {exc}")
        else:
            status.flash(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _set_loading(self, loading: bool) -> None:
        self._loading = loading
        if loading:
            self.query_one("#current", CurrentQuestion).show_loading()
