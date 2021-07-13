""" Converters for types in the Standard Library """
from typing import Type
from enum import Enum
from pathlib import Path

from arc.errors import ConversionError
from arc.types.type_store import register
from .base_converter import BaseConverter

__all__ = ["EnumConverter", "PathConverter"]


def enum_name(enum: "EnumConverter") -> str:
    return "enum"


@register(Enum, enum_name)
class EnumConverter(BaseConverter[Type[Enum]]):
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
