import typing as t
from abc import ABC, abstractmethod

import arc
from arc import constants, errors
from arc.color import colorize, fg, fx
from arc.present import Join
from arc.prompt.helpers import ARROW_DOWN, ARROW_UP, State

T = t.TypeVar("T")
C = t.TypeVar("C")


class QuestionError(errors.ArcError):
    ...


class BaseQuestion(ABC, t.Generic[T]):
    """Base Question class"""

    def err(self, error: str) -> t.NoReturn:
        """Inform the user that an error has
        occured when trying to process their answer"""
        raise QuestionError(error)

    @abstractmethod
    def render(self) -> t.Iterable[str]:
        """Returns an iterable of strings
        to be printed to the output"""


class Question(BaseQuestion[T], ABC):
    def __init__(self, echo: bool = True) -> None:
        self.echo = echo

    @abstractmethod
    def handle_answer(self, value: str) -> T:
        ...


class InputQuestion(Question[T]):
    """Question to request textual input from the user.
    Similar to using `input()` with add validations.

    `Prompt.input()` is an alias for asking this question
    """

    def __init__(
        self,
        prompt: str,
        convert: type[T] = str,  # type: ignore
        *,
        default: T | constants.Constant = constants.MISSING_DEFAULT,
        echo: bool = True,
    ) -> None:
        """

        Args:
            prompt (str): String to be displayed before the cursor
            convert (type[T], optional): A type to attempt converting
                the user input into. Should be a supported arc type. If
                conversion fails, an error will be emmited and the user
                will be prompted to enter a value again.
            default (T | constants.Constant, optional): A default to return
                if the user does not enter any input (just hits the enter key).
                If there is no default provided, the user must give some form of
                input, or exit the program with Ctrl-C
            echo (bool, optional): Whether to echo the user's input out to the screen.
        """
        super().__init__(echo)
        self.prompt = prompt
        self.convert_to = convert
        self.default = default

    def render(self) -> t.Iterable[str]:
        yield self.prompt

    def handle_answer(self, value: str) -> T:
        if not value:
            if self.default is not constants.MISSING_DEFAULT:
                return t.cast(T, self.default)
            else:
                self.err("Cannot be blank")

        value = self.validate(value)
        return self.convert(value, self.convert_to)

    def validate(self, value: str) -> t.Any:
        return value

    def convert(self, value: str, type: type[C]) -> C:
        try:
            return arc.convert(value, type)
        except errors.ConversionError as e:
            self.err(str(e))


class RangeQuestion(InputQuestion[int]):
    """Question for a number in a given range"""

    def __init__(self, prompt: str, min: int, max: int, **kwargs: t.Any):
        """
        Args:
            min: the smallest number possible
            max: the largest  number possible
        """
        super().__init__(prompt, convert=int, **kwargs)
        self.min = min
        self.max = max

    def validate(self, answer: str) -> int:
        val = self.convert(answer, int)
        if val < self.min or val > self.max:
            self.err(f"Must be between {self.min} and {self.max}")

        return val


class MappedInputQuestion(InputQuestion[T]):
    def __init__(
        self,
        prompt: str,
        mapping: t.Mapping[str, T],
        **kwargs: t.Any,
    ) -> None:
        super().__init__(prompt, **kwargs)
        self.mapping = mapping

    def validate(self, answer: str) -> T:
        if answer.lower() in self.mapping:
            return self.mapping[answer.lower()]

        self.err(
            f"Please enter {Join.with_or(list(self.mapping.keys()))}",
        )


class ConfirmQuestion(MappedInputQuestion[bool]):
    """Question to get a yes / no from the user

    `Prompt.confirm()` is an alias for asking this question
    """

    def __init__(self, prompt: str, **kwargs: t.Any) -> None:
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

    def __init__(self, prompt: str, choices: list[str], **kwargs: t.Any):
        super().__init__(prompt, **kwargs)
        self.choices = choices

    def render(self) -> t.Iterable[str]:
        yield self.prompt + "\n"

        for idx, choice in enumerate(self.choices):
            yield f"[{idx}] {choice}\n"

        yield "> "

    def validate(self, answer: str) -> tuple[int, str]:
        val = self.convert(answer, int)

        if val < 0 or val >= len(self.choices):
            self.err("Input not in range")

        return val, self.choices[val]


class RawQuestion(BaseQuestion[T]):
    def __init__(self) -> None:
        self.is_done = False
        self.result: T | None = None
        self.update_occured = False

    def on_key(self, key: str) -> None:
        ...

    def on_line(self, line: str) -> None:
        ...

    def on_done(self, content: str) -> None:
        ...

    def done(self, value: T | None = None) -> None:
        self.is_done = True
        self.result = value


class SelectQuestion(RawQuestion[tuple[int, T]]):
    """Presents the user with a menu that they can select an option from

    `Prompt.select()` is an alias for asking this question
    """

    selected = State(0)

    def __init__(
        self, prompt: str, options: list[T], highlight_color: str = fg.ARC_BLUE
    ) -> None:
        super().__init__()
        self.prompt = prompt
        self.char = "❯"
        self.options = options
        self.highlight_color = highlight_color

    def on_key(self, key: str) -> None:
        if key == ARROW_UP:
            self.selected = max(0, self.selected - 1)
        elif key == ARROW_DOWN:
            self.selected = min(len(self.options) - 1, self.selected + 1)
        elif key.isnumeric():
            index = int(key)
            if index < len(self.options):
                self.selected = index

    def on_line(self, _line: str) -> None:
        self.done((self.selected, self.options[self.selected]))

    def render(self) -> t.Iterable[str]:
        yield self.prompt
        yield "\n\r"
        for idx, item in enumerate(self.options):
            if idx == self.selected:
                yield colorize(f"  {self.char} {item}", self.highlight_color)
            else:
                yield colorize(f"    {item}", fg.GREY)

            yield "\r\n"
