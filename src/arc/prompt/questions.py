from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union
from arc.color import fg, effects

T = TypeVar("T")

# Validators


def is_int(f):
    """Asserts that the given answer is a number.
    If it is a number, cast to an int and call
    the decorated function.
    """

    def wrapper(inst, answer: str, *args, **kwargs):
        if not answer.isnumeric():
            raise QuestionError("Input must be a number")

        return f(inst, int(answer), *args, **kwargs)

    return wrapper


def is_list(f):
    """Splits the answer on commas"""

    def wrapper(inst, answer: str, *args, **kwargs):
        return f(inst, list(a.strip() for a in answer.split(",")), *args, **kwargs)

    return wrapper


class QuestionError(Exception):
    ...


class Question(ABC, Generic[T]):
    @abstractmethod
    def render(self) -> str:
        """Returns a string repersentation of the question"""

    @abstractmethod
    def handle_answer(self, answer: str) -> T:
        """Handles the user's input for the question"""


MultipleReturn = Union[tuple[int, str], list[tuple[int, str]]]


class MultipleChoiceQuestion(Question[MultipleReturn]):
    """Question with multiple possible options

    ```
    MultipleChoiceQuestion(["Option 1", "Option 2", "Option 3",])
    [0] Option 1
    [1] Option 2
    [3] Option 3
    ```

    if `multiple_answer = True`, the user can choose multiple options (1,2,3)
    """

    def __init__(self, choices: list[str], multiple_answer: bool = False):
        self.choices = choices
        self.multiple_answer = multiple_answer

    def render(self) -> str:
        choices = "\n".join(
            f"[{idx}] {choice}" for idx, choice in enumerate(self.choices)
        )

        return choices + self._render_multiple_answer()

    def _render_multiple_answer(self) -> str:
        if not self.multiple_answer:
            return ""

        return "\nMultiple answers can be selected (i.e: 1,2,3)"

    def handle_answer(self, answer: str):
        if self.multiple_answer:
            return self._handle_multiple_answer(answer)
        return self._handle_single_answer(answer)

    @is_int
    def _handle_single_answer(self, answer: int):
        if answer >= len(self.choices):
            raise QuestionError("Input not in range")

        return (answer, self.choices[answer])

    @is_list
    def _handle_multiple_answer(self, answer: list[str]):
        return list(self._handle_single_answer(a) for a in answer)


class RangeQuestion(Question[int]):
    """Question for a number in a given range"""

    def __init__(self, min: int, max: int):
        """
        :param min: the smallest number possible
        :param max: the largest  number possible
        """
        self.min = min
        self.max = max

    def render(self) -> str:
        return f"Pick a number between {self.min} and {self.max}"

    @is_int
    def handle_answer(self, answer: int):
        if answer < self.min or answer > self.max:
            raise QuestionError("Input not in range")

        return answer


class ConfirmQuestion(Question[bool]):
    """Question to get a yes / no from the user

    `confirm()` is an alias for asking this question
    """

    result = {
        "y": True,
        "yes": True,
        "n": False,
        "no": False,
    }

    def __init__(self, message: str):
        self.message = message

    def render(self) -> str:
        return f"{self.message} [{fg.GREEN}Y{effects.CLEAR}/{fg.RED}N{effects.CLEAR}]"

    def handle_answer(self, answer: str) -> bool:
        if answer.lower() in self.result:
            return self.result[answer.lower()]

        raise QuestionError(
            "Not valid, please enter "
            f"{fg.GREEN}y{effects.CLEAR} or {fg.RED}n{effects.CLEAR}",
        )