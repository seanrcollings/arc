from typing import Any
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    """Base Converter, all converters must inherit from this converter"""

    def __init__(self, annotation):
        self.annotation = annotation

    @abstractmethod
    def convert(self, value: str) -> Any:
        """ Method that converts the string sent, to it's desired type."""

    @property
    @abstractmethod
    def convert_to(self):
        """Specifies conversion type

        String that specifies what type the
        converter is supposed to convert the
        value into
        """


class TypeConverter:
    convert_to: type

    def convert(self, value: str):
        return self.convert_to(value)
