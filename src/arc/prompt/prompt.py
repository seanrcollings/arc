import functools
from typing import Any, TypeVar

from arc.color import fg, effects
from .helpers import write, CLEAR_LINE, PREVIOUS_LINE
from .confirm import confirm
from .questions import Question, QuestionError


V = TypeVar("V")


def colorize(f):
    @functools.wraps(f)
    def wrapper(inst: "Prompt", message: str, *args, **kwargs):
        color, emoji = f(inst, message)
        print(color + inst.emoji(emoji) + message + effects.CLEAR, *args, **kwargs)

    return wrapper


class Prompt:
    def __init__(self, show_emojis: bool = True):
        self.show_emojis = show_emojis
        self._previous_answers: list[Any] = []

    @property
    def previous_answers(self):
        return self._previous_answers

    def ask(self, question: Question[V], description: str = None) -> V:
        if description:
            print(description)

        print(question.render())
        answer = None
        while not answer:
            user_input = input(f"\n{CLEAR_LINE}> ").lower()
            try:
                answer = question.handle_answer(user_input)
            except QuestionError as e:
                write(f"{PREVIOUS_LINE}{PREVIOUS_LINE}{e}")

        self._previous_answers.append(answer)
        return answer

    def confirm(self, *args, **kwargs):
        answer = confirm(*args, **kwargs)
        self._previous_answers.append(answer)
        return answer

    @colorize
    def error(self, _message: str):
        return fg.RED, "🚨"

    @colorize
    def ok(self, _message: str):
        return fg.GREEN, "✓"

    @colorize
    def no(self, _message: str):
        return fg.RED, "✗"

    @colorize
    def act(self, _message: str):
        return fg.BLUE.bright, ""

    @colorize
    def warn(self, _message: str):
        return fg.YELLOW, "🚧"

    @colorize
    def subtle(self, _message: str):
        return fg.GREY, ""

    def emoji(self, emoji: str):
        if self.show_emojis and len(emoji) > 0:
            return emoji + " "
        return ""
