from typing import Any
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    """Base Converter, all converters must inherit from this converter"""

    def __init__(self, annotation):
        self.annotation = annotation

    def convert(self, value: str) -> Any:
        """ Method that converts the string sent, to it's desired type."""
        return self.convert_to(value)

    @property
    @abstractmethod
    def convert_to(self):
        """Specifies conversion type

        String that specifies what type the
        converter is supposed to convert the
        value into
        """
