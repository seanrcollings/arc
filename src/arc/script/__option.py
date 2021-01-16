from typing import Any
import inspect

from arc import config
from arc.convert import is_alias
from arc.utils import symbol, Helpful
from arc.types import needs_cleanup, ArcGeneric


NO_DEFAULT = symbol("NO_DEFAULT")
# pylint: disable=protected-access
EMPTY = inspect._empty  # type: ignore


class Option(Helpful):
    def __init__(self, name, annotation, default):
        self.name = name
        self.annotation = Any if annotation is EMPTY else annotation
        self.default = NO_DEFAULT if default is EMPTY else default
        self.value = self.default

    def __repr__(self):
        return f"<Option : {self.name}>"

    def convert(self):
        """Converts self.value using the converter found by get_converter"""
        if self.annotation is Any:
            return

        name = self.get_converter_name()
        converter = config.get_converter(name)

        self.value = converter(self.annotation).convert_wrapper(self.value)

    def get_converter_name(self) -> str:
        """Returns the converter name for
        the option's annotation
        """
        # Move this logic into convert.get_converter() ?
        if is_alias(self.annotation):
            if issubclass(self.annotation.__origin__, ArcGeneric):  # type: ignore
                return self.annotation.__origin__.__name__.lower()  # type: ignore
            else:
                return "alias"
        return self.annotation.__name__

    def cleanup(self):
        # Any special types need to implement
        # the __del__ magic method to preform cleanup
        if needs_cleanup(self.annotation):
            del self.value

    def helper(self):
        print(f"{self.name}{config.options_seperator}{self.default}")
