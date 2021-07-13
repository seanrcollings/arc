""" Converters for types in the Standard Library """
from enum import Enum
from pathlib import Path

from arc.errors import ConversionError
from arc.types.type_store import register
from .base_converter import BaseConverter

__all__ = ["EnumConverter", "PathConverter"]


def format_enum(enum: type[Enum]) -> str:
    vals = [member.value for member in enum.__members__.values()]
    return ", ".join(vals[:-1]) + f" or {vals[-1]}"


@register(Enum, format_enum)
class EnumConverter(BaseConverter[type[Enum]]):
    def convert(self, value):
        if value.isnumeric():
            value = int(value)

        try:
            return self.annotation(value)
        except ValueError as e:
            raise ConversionError(
                value,
                expected=f"to be: {', '.join(str(data.value) for data in self.annotation)}",
            ) from e


@register(Path, "filepath")
class PathConverter(BaseConverter[Path]):
    def convert(self, value: str) -> Path:
        return Path(value)
