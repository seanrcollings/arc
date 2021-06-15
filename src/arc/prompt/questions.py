from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class QuestionError(Exception):
    ...


class Question(ABC, Generic[T]):
    @abstractmethod
    def render(self) -> str:
        """Returns a string repersentation of the question"""

    @abstractmethod
    def handle_answer(self, answer: str) -> T:
        """Handles the user's input for the question"""


class MultipleChoiceQuestion(Question[tuple[int, str]]):
    def __init__(self, choices: list[str]):
        self.choices = choices

    def render(self) -> str:
        return "\n".join(f"[{idx}] {choice}" for idx, choice in enumerate(self.choices))

    def handle_answer(self, answer: str):
        if not answer.isnumeric():
            raise QuestionError("Input must be a number")

        idx = int(answer)

        if idx >= len(self.choices):
            raise QuestionError("Input not in range")

        return (idx, self.choices[idx])


class RangeQuestion(Question[int]):
    ...
