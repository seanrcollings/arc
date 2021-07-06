import inspect
import enum

from arc.config import config
from arc.utils import symbol
from arc.convert import convert


NO_DEFAULT = symbol("NO_DEFAULT")
# pylint: disable=protected-access
EMPTY = inspect._empty  # type: ignore


class Argument:
    def __init__(
        self, name, annotation, default, hidden=False, aliases: set[str] = None
    ):
        self.name: str = name
        self.annotation = str if annotation is EMPTY else annotation
        self.default = NO_DEFAULT if default is EMPTY else default
        self.hidden = hidden
        # Aliases are optional secondary names for arguments
        # currently only used to store shorter names for flags
        self.aliases = aliases or set()

    def __repr__(self):
        return f"<Argument : {self.name}={self.default}>"

    def convert(self, value: str):
        """Converts the provided value to the expected value of the argument"""
        if self.annotation is str:
            return value

        return convert(value, self.annotation, self.name)

    def is_flag(self):
        return self.annotation is bool

    def is_optional(self):
        return self.default is not NO_DEFAULT
