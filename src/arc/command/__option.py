import inspect

from arc import arc_config
from arc.utils import symbol, Helpful
from arc.types import needs_cleanup
from arc.convert import convert


NO_DEFAULT = symbol("No Default")
# pylint: disable=protected-access
EMPTY = inspect._empty  # type: ignore


class Option(Helpful):
    def __init__(self, name, annotation, default):
        self.name: str = name
        self.annotation = str if annotation is EMPTY else annotation
        self.default = NO_DEFAULT if default is EMPTY else default
        self.value = self.default

    def __repr__(self):
        return f"<Option : {self.name}={self.value}>"

    def convert(self):
        """Converts self.value using the
        converter associated with self.annotation"""
        if self.annotation is str:
            return

        self.value = convert(self.value, self.annotation, self.name)

    def cleanup(self):
        # Any special types need to implement
        # the __del__ magic method to preform cleanup
        if needs_cleanup(self.annotation):
            del self.value

    def helper(self, level: int = 0):
        print(f"{self.name}{arc_config.arg_assignment}{self.default}")
