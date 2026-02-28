from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label, Static


class QuestionHistory(ListView):
    """Append-only log of past Q&A pairs."""

    def append_qa(self, step: int, question: str, key: str) -> None:
        key_labels = {
            "y": "Yes", "n": "No", "?": "IDK",
            "+": "Probably", "-": "Probably not", "b": "Back",
        }
        label = key_labels.get(key, key)
        self.append(ListItem(Label(f"[bold]{step}.[/bold] {question}  →  [italic]{label}[/italic]")))
        self.scroll_end(animate=False)

    def append_win(self, name: str, outcome: str) -> None:
        self.append(ListItem(Label(f"[bold green]{name}[/bold green]  →  {outcome}")))
        self.scroll_end(animate=False)


class CurrentQuestion(Static):
    """Displays the current question or a loading indicator."""

    DEFAULT_CSS = """
    CurrentQuestion {
        height: auto;
        min-height: 3;
        border: round $accent;
        padding: 0 1;
    }
    """

    def show_question(self, step: int, question: str) -> None:
        self.update(f"[bold]{step + 1}.[/bold] {question}")

    def show_loading(self) -> None:
        self.update("[dim]Thinking...[/dim]")

    def show_win_prompt(self, name: str, desc: str) -> None:
        self.update(
            f"[bold yellow]I think it's:[/bold yellow] {name}\n"
            f"[dim]{desc}[/dim]\n"
            "Am I right? [bold][y][/bold]es / [bold][n][/bold]o"
        )

    def show_result(self, message: str) -> None:
        self.update(message)


class WinProposal(Static):
    """Shown when aki.win is True. Hidden otherwise."""

    DEFAULT_CSS = """
    WinProposal {
        display: none;
        height: auto;
        border: round $success;
        padding: 0 1;
    }
    """

    def show(self, name: str, desc: str) -> None:
        self.display = True
        self.update(
            f"[bold green]I think it's:[/bold green] [bold]{name}[/bold]\n"
            f"[dim]{desc}[/dim]"
        )

    def hide(self) -> None:
        self.display = False


class StatusBar(Static):
    """Flashes transient error/info messages."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        color: $warning;
    }
    """

    _timer = None

    def flash(self, message: str, duration: float = 3.0) -> None:
        if self._timer is not None:
            self._timer.stop()
        self.update(message)
        self._timer = self.set_timer(duration, self._clear)

    def _clear(self) -> None:
        self.update("")
        self._timer = None
