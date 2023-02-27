import typing as t
from abc import ABC, abstractmethod

import arc
from arc import errors
from arc.color import colorize, fg
from arc.present.helpers import Joiner
from arc.prompt.helpers import ARROW_DOWN, ARROW_UP, State

T = t.TypeVar("T")
C = t.TypeVar("C")


class QuestionError(errors.ArcError):
    ...


class Question(ABC, t.Generic[T]):
    def err(self, error: str) -> t.NoReturn:
        raise QuestionError(error)

    @abstractmethod
    def render(self) -> t.Iterable[str]:
        ...


class StandardQuestion(Question[T], ABC):
    def __init__(self, echo: bool = True) -> None:
        self.echo = echo

    @abstractmethod
    def handle_answer(self, value: str) -> T:
        ...


# TODO: respect the usage of default
class InputQuestion(StandardQuestion[T]):
    def __init__(
        self,
        prompt: str,
        convert: type[T] = str,  # type: ignore
        *,
        default: T | None = None,
        echo: bool = True,
    ) -> None:
        super().__init__(echo)
        self.prompt = prompt
        self.convert_to = convert
        self.default = default

    @property
    def required(self):
        return self.default is None

    def render(self):
        yield self.prompt

    def handle_answer(self, value: str) -> T:
        self.test_required(value)
        return self.convert(value, self.convert_to)

    def convert(self, value: str, type: type[C]) -> C:
        try:
            return arc.convert(value, type)
        except errors.ConversionError as e:
            self.err(str(e))

    def test_required(self, value: str):
        if not value and self.required:
            self.err("Cannot be blank")


class RangeQuestion(InputQuestion[int]):
    """Question for a number in a given range"""

    def __init__(self, prompt: str, min: int, max: int, **kwargs):
        """
        Args:
            min: the smallest number possible
            max: the largest  number possible
        """
        super().__init__(prompt, convert=int, **kwargs)
        self.min = min
        self.max = max

    def handle_answer(self, answer: str) -> int:
        val = super().handle_answer(answer)

        if val < self.min or val > self.max:
            self.err(f"Must be between {self.min} and {self.max}")

        return val


class MappedInputQuestion(InputQuestion[T]):
    def __init__(
        self,
        prompt: str,
        mapping: t.Mapping[str, T],
        **kwargs,
    ) -> None:
        super().__init__(prompt, **kwargs)
        self.mapping = mapping

    def handle_answer(self, answer: str) -> T:
        self.test_required(answer)

        if answer.lower() in self.mapping:
            return self.mapping[answer.lower()]

        self.err(
            f"Please enter {Joiner.with_or(list(self.mapping.keys()))}",
        )


class ConfirmQuestion(MappedInputQuestion[bool]):
    """Question to get a yes / no from the user"""

    def __init__(self, prompt: str, **kwargs) -> None:
        super().__init__(
            prompt,
            mapping={
                "y": True,
                "yes": True,
                "n": False,
                "no": False,
            },
            **kwargs,
        )


class MultipleChoiceQuestion(InputQuestion[tuple[int, str]]):
    """Question with multiple possible options

    ```
    MultipleChoiceQuestion(["Option 1", "Option 2", "Option 3",])
    [0] Option 1
    [1] Option 2
    [3] Option 3
    ```
    """

    def __init__(self, prompt: str, choices: list[str], **kwargs):
        super().__init__(prompt, **kwargs)
        self.choices = choices

    def render(self):
        yield self.prompt + "\n"

        for idx, choice in enumerate(self.choices):
            yield f"[{idx}] {choice}\n"

        yield "> "

    def handle_answer(self, answer: str) -> tuple[int, str]:
        self.test_required(answer)
        val = self.convert(answer, int)

        if val < 0 or val >= len(self.choices):
            self.err("Input not in range")

        return val, self.choices[val]


class RawQuestion(Question[T]):
    def __init__(self) -> None:
        self.is_done = False
        self.result: T | None = None
        self.update_occured = False

    def on_key(self, key: str):
        ...

    def on_line(self, line: str):
        ...

    def on_done(self, content: str):
        ...

    def done(self, value: T | None = None):
        self.is_done = True
        self.result = value


class SelectQuestion(RawQuestion[tuple[int, T]]):
    selected = State(0)

    def __init__(
        self, prompt: str, options: list[T], highlight_color: str = fg.ARC_BLUE
    ) -> None:
        super().__init__()
        self.prompt = prompt
        self.char = "❯"
        self.options = options
        self.highlight_color = highlight_color

    def on_key(self, key: str):
        if key == ARROW_UP:
            self.selected = max(0, self.selected - 1)
        elif key == ARROW_DOWN:
            self.selected = min(len(self.options) - 1, self.selected + 1)

    def on_line(self, _line):
        self.done((self.selected, self.options[self.selected]))

    def render(self):
        yield self.prompt
        yield "\n\r"
        for idx, item in enumerate(self.options):
            if idx == self.selected:
                yield colorize(f"  {self.char} {item}", self.highlight_color)
                yield "\n\r"
            else:
                yield colorize(f"    {item}", fg.GREY)
                yield "\n\r"
