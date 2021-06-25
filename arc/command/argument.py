import inspect

from arc import config
from arc.utils import symbol
from arc.types import needs_cleanup
from arc.convert import convert


NO_DEFAULT = symbol("NO_DEFAULT")
# pylint: disable=protected-access
EMPTY = inspect._empty  # type: ignore


class Argument:
    def __init__(self, name, annotation, default, hidden=False):
        self.name: str = name
        self.annotation = str if annotation is EMPTY else annotation
        self.default = NO_DEFAULT if default is EMPTY else default
        self.hidden = hidden

    def __repr__(self):
        return f"<Argument : {self.name}={self.default}>"

    def convert(self, value: str):
        """Converts the provided value to the expected value of the argument"""
        if self.annotation is str:
            return value

        return convert(value, self.annotation, self.name)

    def helper(self, level: int = 0):
        print(f"{self.name}{config.arg_assignment}{self.default}")
