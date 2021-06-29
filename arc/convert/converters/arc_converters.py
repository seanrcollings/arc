""" Converters For Special Arc Types """
from typing import Optional

from arc.types import File, Range, ValidPath
from arc import errors, utils
from .base_converter import BaseConverter
from .converter_mapping import register

__all__ = ["FileConverter", "RangeConverter", "ValidPathConverter"]


@register(File)
class FileConverter(BaseConverter[File]):
    """Converts a string to a file handler object
    /path/to/a/file
    """

    def convert(self, value):
        return self.annotation(value, self.annotation.__args__).open()


@register(Range)
class RangeConverter(BaseConverter[Range]):
    _range: Optional[tuple[int, int]] = None

    def convert(self, value: str):
        error = errors.ConversionError(
            value,
            f"an integer in range: {self.range}",
            "Note that the range is inclusive on the minimum and exclusive on the maximum",
        )

        if not value.isnumeric():
            raise error

        int_value = int(value)
        smallest, largest = self.range
        if not (int_value >= smallest and int_value < largest):
            raise error

        return Range(int_value, smallest, largest)

    @property
    def range(self):
        if self._range is None:
            smallest, largest = self.annotation.__args__
            if utils.is_alias(smallest):
                smallest = smallest.__args__[0]
            if utils.is_alias(largest):
                largest = largest.__args__[0]

            if isinstance(smallest, int) and isinstance(largest, int):
                self._range = smallest, largest
            else:
                raise errors.ArcError(
                    f"The min and max of a range must be integers: {smallest, largest}"
                )

        return self._range


@register(ValidPath)
class ValidPathConverter(BaseConverter[ValidPath]):
    def convert(self, value: str) -> ValidPath:
        path = ValidPath(value)
        if not path.exists():
            raise errors.ConversionError(value, "a valid filepath")
        return path
