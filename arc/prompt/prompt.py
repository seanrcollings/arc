import sys
import typing as t
from getpass import getpass

from arc.color import colorize, fg, effects
from arc.context import Context
from .helpers import (
    CTRL_C,
    ESCAPE,
    Cursor,
    RawTerminal,
    clear_line,
)
from .questions import (
    ConfirmQuestion,
    Question,
    QuestionError,
    InputQuestion,
    RawQuestion,
    StandardQuestion,
)


T = t.TypeVar("T")


class Prompt:
    def __init__(self, show_emojis: bool = True, color_output: bool = True) -> None:
        self.out_stream = sys.stdout
        self.show_emojis = show_emojis
        self.color_output = color_output
        self._buffer: str = ""
        self._prev_buffer: str = ""
        self._answers: list[tuple[Question, t.Any]] = []
        self._max_line_lengths: dict[int, int] = {}

    @property
    def answers(self) -> list[tuple[Question, t.Any]]:
        return self._answers

    def ask(self, question: Question[T]) -> T:
        if isinstance(question, RawQuestion):
            return self._raw_ask(question)
        elif isinstance(question, StandardQuestion):
            return self._standard_ask(question)

        raise RuntimeError("Called Prompt.ask() with an invalid question object")

    @t.overload
    def input(self, prompt: str, **kwargs) -> str:
        ...

    @t.overload
    def input(self, prompt: str, convert: type[T], **kwargs) -> T:
        ...

    def input(self, prompt, convert=str, **kwargs):
        question = InputQuestion(prompt, convert, **kwargs)
        return self.ask(question)

    def confirm(self, prompt, **kwargs):
        prompt = f"{prompt} [{colorize('y', fg.GREEN)}/{colorize('n', fg.RED)}] "
        question = ConfirmQuestion(prompt, **kwargs)
        return self.ask(question)

    def _standard_ask(self, question: StandardQuestion):
        answer = None
        get_input: t.Callable[[], str] = input if question.echo else lambda: getpass("")  # type: ignore
        self.write_many(question.render())

        self.flush()
        row, col = Cursor.getpos()

        while answer is None:
            self.write(clear_line("after"))
            self.flush()
            user_input = get_input()

            try:
                answer = question.handle_answer(user_input)
            except QuestionError as e:
                self.write(clear_line())
                self.error(str(e))
                Cursor.setpos(row, col)

        self.write(clear_line())
        self.flush()
        self._answers.append((question, answer))
        return answer

    def _raw_ask(self, question: RawQuestion):
        Cursor.save()
        self.write_many(question.render())
        self.flush()

        full_input: list[str] = [""]
        with RawTerminal() as term:
            while True:
                if question.is_done:
                    question.on_done("\n".join(full_input))
                    break

                if question.update_occured and self.should_update():
                    Cursor.restore()
                    Cursor.save()
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
        self._buffer = ""
        self._prev_buffer = ""
        result = question.result
        question.result = None
        self._answers.append((question, result))
        return result

    def write(self, value: t.Any):
        text = str(value)
        self._buffer += text
        if text.endswith("\n"):
            self.flush()

    def write_many(self, values: t.Iterable):
        for v in values:
            self.write(v)

    def flush(self):
        self.out_stream.write("".join(self._buffer))
        self.out_stream.flush()
        self._buffer = ""

    def cycle_buffers(self):
        self._prev_buffer = self._buffer
        self._buffer = ""

    def should_update(self) -> bool:
        return self._buffer != self._prev_buffer

    def get_key(self, term: RawTerminal):
        seq = term.getch()
        if seq == ESCAPE:
            seq += term.getch()  # [
            seq += term.getch()  # Some Character
            return seq
        elif seq == "\r":
            return "\r\n"
        elif seq == CTRL_C:
            raise RuntimeError()
        else:
            return seq

    def beautify(self, message: str, color: str = "", emoji: str = "", end: str = "\n"):
        self.write(
            self.colored(color) + self.emoji(emoji) + message + effects.CLEAR + end
        )

    def error(self, message: str, **kwargs):
        """Display an error message to the user"""
        self.beautify(message, fg.RED, "🚨", **kwargs)

    def ok(self, message: str, **kwargs):
        """Display a successful message to the user"""
        self.beautify(message, fg.GREEN, "✓", **kwargs)

    def no(self, message: str, **kwargs):
        """Display an unsuccessful message to the user"""
        self.beautify(message, fg.RED, "✗", **kwargs)

    def act(self, message: str, **kwargs):
        """Display an action message to the user"""
        self.beautify(message, fg.BRIGHT_BLUE, **kwargs)

    def warn(self, message: str, **kwargs):
        """Display a warning message to the user"""
        self.beautify(message, fg.YELLOW, "🚧", **kwargs)

    def subtle(self, message: str, **kwargs):
        """Display a subtle (light grey) message to the user"""
        self.beautify(message, fg.GREY, **kwargs)

    def snake(self, message: str, **kwargs):
        """Display a Pythonic message to the user"""
        self.beautify(message, emoji="🐍", **kwargs)

    def emoji(self, emoji: str):
        if self.show_emojis and len(emoji) > 0:
            return emoji + " "
        return ""

    def colored(self, color: str):
        if self.color_output:
            return color
        return ""

    @classmethod
    def __depends__(self, ctx: Context) -> "Prompt":
        return ctx.config.prompt
