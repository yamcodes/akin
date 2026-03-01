from __future__ import annotations

from rich.markup import escape
from textual.widgets import Label, ListItem, ListView, Static


class QuestionHistory(ListView):
    """Append-only log of past Q&A pairs."""

    def append_qa(self, step: int, question: str, key: str) -> None:
        key_labels = {
            "y": "Yes", "n": "No", "?": "IDK",
            "+": "Probably", "-": "Probably not", "b": "Back",
        }
        label = key_labels.get(key, key)
        self.append(ListItem(Label(f"[dim]{step}.[/dim] {escape(question)}  [dim]→ {escape(label)}[/dim]")))
        self.scroll_end(animate=False)

    def append_win(self, name: str, outcome: str) -> None:
        self.append(ListItem(Label(f"[bold]{escape(name)}[/bold]  [dim]→ {escape(outcome)}[/dim]")))
        self.scroll_end(animate=False)


class CurrentQuestion(Static):
    """Displays the current question or a loading indicator."""

    def show_question(self, step: int, question: str) -> None:
        self.update(f"[dim]{step + 1}.[/dim] {escape(question)}")

    def show_loading(self) -> None:
        self.update("[dim]...[/dim]")

    def show_win_prompt(self, name: str, desc: str) -> None:
        self.update(
            f"[bold]{escape(name)}[/bold]\n"
            f"[dim]{escape(desc)}[/dim]\n\n"
            "[dim]Is that right?[/dim]  [bold]y[/bold]es / [bold]n[/bold]o"
        )

    def show_result(self, message: str) -> None:
        self.update(message)


class WinProposal(Static):
    """Shown when aki.win is True. Hidden otherwise."""

    def show(self, name: str, desc: str) -> None:
        self.display = True
        self.update(
            f"[bold]{escape(name)}[/bold]\n"
            f"[dim]{escape(desc)}[/dim]"
        )

    def hide(self) -> None:
        self.display = False


class StatusBar(Static):
    """Flashes transient error/info messages."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._timer = None

    def flash(self, message: str, duration: float = 3.0) -> None:
        if self._timer is not None:
            self._timer.stop()
        self.update(escape(message))
        self._timer = self.set_timer(duration, self._clear)

    def _clear(self) -> None:
        self.update("")
        self._timer = None
