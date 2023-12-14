from __future__ import annotations

import os
import sys
import typing as t
from getpass import getpass

from arc.color import fg, fx
from arc.present.ansi import colorize

from .helpers import CTRL_C, ESCAPE, Cursor, RawTerminal, clear_line
from .questions import (
    BaseQuestion,
    ConfirmQuestion,
    InputQuestion,
    Question,
    QuestionError,
    RawQuestion,
    SelectQuestion,
)

if t.TYPE_CHECKING:
    from arc.runtime import Context

T = t.TypeVar("T")


class Prompt:
    def __init__(self) -> None:
        self.out_stream = sys.stdout
        self._buffer: list[str] = []
        self._prev_buffer: list[str] = []
        self._answers: list[tuple[BaseQuestion[t.Any], t.Any]] = []
        self._max_line_lengths: dict[int, int] = {}

    @property
    def answers(self) -> list[tuple[BaseQuestion[t.Any], t.Any]]:
        return self._answers

    @property
    def buffered_lines(self) -> int:
        count = 0
        for string in self._buffer:
            for char in string:
                if char == "\n":
                    count += 1
        return count

    def ask(self, question: BaseQuestion[T]) -> T:
        if isinstance(question, RawQuestion):
            return self._raw_ask(question)
        elif isinstance(question, Question):
            return self._standard_ask(question)

        raise RuntimeError("Called Prompt.ask() with an invalid question object")

    @t.overload
    def input(self, prompt: str, **kwargs: t.Any) -> str:
        ...

    @t.overload
    def input(self, prompt: str, convert: type[T], **kwargs: t.Any) -> T:
        ...

    def input(self, prompt: str, convert: type = str, **kwargs: t.Any) -> t.Any:
        """Get input from the user"""
        question = InputQuestion[str](prompt, convert, **kwargs)
        return self.ask(question)

    def confirm(self, prompt: str, **kwargs: t.Any) -> bool:
        """Get a yes / no confirmation from the user"""
        prompt = f"{prompt} [{colorize('y', fg.GREEN)}/{colorize('n', fg.RED)}] "
        question = ConfirmQuestion(prompt, **kwargs)
        return self.ask(question)

    def select(
        self,
        prompt: str,
        options: t.Sequence[tuple[T, str]],
        **kwargs: t.Any,
    ) -> T:
        """Prompt the user to select from a list of options

        Args:
            prompt (str): The prompt to display to the user
            options (t.Sequence[tuple[T, str]]): A list of tuples containing the options.
            The first entry of the tuple is the value that will be returned, and the second
            is the text that will be displayed to the user

        Returns:
            T: The value of the selected option

        """
        question = SelectQuestion(prompt, options, **kwargs)
        return self.ask(question)

    def _standard_ask(self, question: Question[t.Any]) -> t.Any:
        answer = None
        get_input: t.Callable[[], str] = input if question.echo else lambda: getpass("")  # type: ignore
        self.write_many(question.render())
        self.flush()
        row, col = Cursor.getpos()
        self.write("\r\n", flush=True)
        row, col = self.ensure_space(row, col)
        Cursor.setpos(row, col)

        while answer is None:
            self.write(clear_line("after"))
            self.flush()
            user_input = get_input()

            try:
                answer = question.handle_answer(user_input)
            except QuestionError as e:
                self.write(clear_line())
                self.error(str(e), flush=True)
                Cursor.setpos(row, col)

        self.write(clear_line())
        self.flush()
        self._answers.append((question, answer))
        return answer

    def _raw_ask(self, question: RawQuestion[t.Any]) -> t.Any:
        row, col = Cursor.getpos()
        self.write_many(question.render())
        new_row, col = self.ensure_space(row, col)
        self.scroll_terminal(new_row - row - 1)
        self.flush()
        row = new_row
        Cursor.setpos(row, col)

        full_input: list[str] = [""]
        with Cursor.hide(), RawTerminal() as term:
            while True:
                if question.is_done:
                    question.on_done("\n".join(full_input))
                    break

                if question.update_occured:
                    Cursor.setpos(row, col)
                    self.cycle_buffers()
                    self.write_many(question.render())
                    self.flush()

                key = self.get_key(term)
                full_input[-1] += key

                if key.endswith("\n"):
                    question.on_line(full_input[-1])
                    full_input.append("")
                else:
                    question.on_key(key)

        self.write("\n")
        self.clear_buffers()
        result = question.result
        question.result = None
        self._answers.append((question, result))
        return result

    def ensure_space(self, curr_row: int, curr_col: int) -> tuple[int, int]:
        total_rows = self.max_height()
        diff = total_rows - curr_row
        buffered_lines = self.buffered_lines

        if diff < buffered_lines:
            new_lines = buffered_lines - diff
            curr_row -= new_lines

        return curr_row, curr_col

    def max_height(self) -> int:
        return os.get_terminal_size()[1]

    def write(self, value: t.Any, flush: bool = False) -> None:
        text = str(value)
        self._buffer.append(text)
        if flush:
            self.flush()

    def write_front(self, value: t.Any) -> None:
        self._buffer.insert(0, str(value))

    def write_many(self, values: t.Iterable[t.Any]) -> None:
        for v in values:
            self.write(v)

    def flush(self) -> None:
        self.out_stream.write("".join(self._buffer))
        self.out_stream.flush()
        self._buffer = []

    def cycle_buffers(self) -> None:
        self._prev_buffer = self._buffer
        self._buffer = []

    def clear_buffers(self) -> None:
        self._prev_buffer = []
        self._buffer = []

    def scroll_terminal(self, lines: int) -> None:
        self.write(f"\x1b[{lines}S")

    def should_update(self) -> bool:
        return self._buffer != self._prev_buffer

    def get_key(self, term: RawTerminal) -> str:
        seq = term.getch()
        if seq == ESCAPE:
            seq += term.getch()  # [
            seq += term.getch()  # Some Character
            return seq
        elif seq == "\r":
            return "\r\n"
        elif seq == CTRL_C:
            raise SystemExit(1)
        else:
            return seq

    def error(self, message: str, **kwargs: t.Any) -> None:
        self.write(f"{fg.RED}✗ {message}{fx.CLEAR}", **kwargs)

    @classmethod
    def __depends__(self, ctx: Context) -> "Prompt":
        return ctx.prompt
