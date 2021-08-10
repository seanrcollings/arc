import inspect

from arc.utils import symbol
from arc.types import convert


NO_DEFAULT = symbol("NO_DEFAULT")
EMPTY = inspect.Parameter.empty


class Argument:
    def __init__(self, name, annotation, default, hidden=False):
        self.name: str = name
        self.annotation = str if annotation is EMPTY else annotation
        self.default = NO_DEFAULT if default is EMPTY else default
        self.hidden = hidden
        self.short: str = ""

    def __repr__(self):
        return f"<Argument : {self.name}={self.default}>"

    def convert(self, value: str):
        """Converts the provided value to the expected value of the argument"""
        if self.annotation is str:
            return value

        return convert(value, self.annotation, self.name)

    def is_flag(self):
        return self.annotation is bool

    def is_option(self):
        return self.default is not NO_DEFAULT

    def is_positional(self):
        return self.default is NO_DEFAULT
