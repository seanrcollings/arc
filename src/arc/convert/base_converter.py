import sys
from typing import Any
from abc import ABC, abstractmethod
from arc.errors import ConversionError


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

    def convert_wrapper(self, value: str):
        """Try except wrapper for conversion method

        Convert method wrapper for catching
        ConversionErrors. Will display the info
        passed to the ConversionError by the
        converter
        """
        try:
            value = self.convert(value)

        except ConversionError as e:
            print(f"Value: {e.value} could not be converted to '{self.convert_to}'")
            if e.helper_text is not None:
                print(e.helper_text)
            sys.exit(1)

        return value
