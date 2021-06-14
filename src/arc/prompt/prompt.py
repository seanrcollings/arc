from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from .helpers import write, CLEAR_LINE, PREVIOUS_LINE

T = TypeVar("T")


class QuestionError(Exception):
    ...


class Question(ABC, Generic[T]):
    def __init__(self, description: str = None):
        self.description = description

    @abstractmethod
    def render(self) -> str:
        """Returns a string repersentation of the question"""

    @abstractmethod
    def handle_answer(self, answer: str) -> T:
        """Handles the user's input for the question"""


class MultipleChoiceQuestion(Question[tuple[int, str]]):
    def __init__(self, choices: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = choices

    def render(self) -> str:
        desc = f"{self.description}\n" if self.description else ""
        choices = "\n".join(
            f"[{idx}] {choice}" for idx, choice in enumerate(self.choices)
        )
        return desc + choices

    def handle_answer(self, answer: str):
        if not answer.isnumeric():
            raise QuestionError("Input must be a number")

        idx = int(answer)

        if idx >= len(self.choices):
            raise QuestionError("Input not in range")

        return (idx, self.choices[idx])


class Prompt:
    def ask(self, question: Question):
        print(question.render())
        while True:
            user_input = input(f"\n{CLEAR_LINE}> ").lower()
            try:
                return question.handle_answer(user_input)
            except QuestionError as e:
                write(f"{PREVIOUS_LINE}{PREVIOUS_LINE}{e}")
