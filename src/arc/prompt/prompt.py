import functools
from typing import Any, TypeVar

from arc.color import fg, effects
from .helpers import write, CLEAR_LINE, PREVIOUS_LINE
from .confirm import confirm
from .questions import Question, QuestionError


V = TypeVar("V")


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
                write(f"{PREVIOUS_LINE}{PREVIOUS_LINE}{CLEAR_LINE}{e}")

        self._previous_answers.append(answer)
        return answer

    def confirm(self, *args, **kwargs):
        answer = confirm(*args, **kwargs)
        self._previous_answers.append(answer)
        return answer

    def beautify(self, message: str, color: str = "", emoji: str = "", **kwargs):
        print(color + self.emoji(emoji) + message + effects.CLEAR, **kwargs)

    def error(self, message: str, **kwargs):
        self.beautify(message, fg.RED, "🚨", **kwargs)

    def ok(self, message: str, **kwargs):
        self.beautify(message, fg.GREEN, "✓", **kwargs)

    def no(self, message: str, **kwargs):
        self.beautify(message, fg.RED, "✗", **kwargs)

    def act(self, message: str, **kwargs):
        self.beautify(message, fg.BLUE.bright, **kwargs)

    def warn(self, message: str, **kwargs):
        self.beautify(message, fg.YELLOW, "🚧", **kwargs)

    def subtle(self, message: str, **kwargs):
        self.beautify(message, fg.GREY, **kwargs)

    def snake(self, message: str, **kwargs):
        self.beautify(message, emoji="🐍", **kwargs)

    def emoji(self, emoji: str):
        if self.show_emojis and len(emoji) > 0:
            return emoji + " "
        return ""
