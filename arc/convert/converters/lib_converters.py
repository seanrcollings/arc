""" Converters for types in the Standard Library """
from typing import Type
from enum import Enum
from pathlib import Path
from arc.errors import ConversionError

from .base_converter import BaseConverter


__all__ = ["EnumConverter", "PathConverter"]


class EnumConverter(BaseConverter[Type[Enum]]):
    def convert(self, value):
        if value.isnumeric():
            value = int(value)

        try:
            return self.annotation(value)
        except ValueError as e:
            raise ConversionError(
                value,
                expected=f"to be one of: {', '.join(str(data.value) for data in self.annotation)}",
            ) from e


class PathConverter(BaseConverter[Path]):
    def convert(self, value: str) -> Path:
        return Path(value)
