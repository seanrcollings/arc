from typing import _SpecialForm as SpecialForms, Union, TypeVar
from pathlib import Path
from enum import Enum

from arc import utils, errors
from arc.types import File, Range, ValidPath

from .base_converter import BaseConverter

# from .builtin_converters import *
# from .lib_converters import *
# from .arc_converters import *
# from .generic_converters import *

converter_mapping: dict[Union[type, SpecialForms], type[BaseConverter]] = {
    #     # builtin types
    #     str: StringConverter,
    #     int: IntConverter,
    #     float: FloatConverter,
    #     bytes: BytesConverter,
    #     bool: BoolConverter,
    #     list: ListConverter,
    #     # stdlib types
    #     Enum: EnumConverter,
    #     Path: PathConverter,
    #     # Custom Types
    #     File: FileConverter,
    #     Range: RangeConverter,
    #     ValidPath: ValidPathConverter,
}


def register(kind: Union[type, SpecialForms]):
    """Registers decorated `cls` as the converter for `kind`"""

    def wrapper(cls: type[BaseConverter]) -> type[BaseConverter]:
        converter_mapping[kind] = cls
        return cls

    return wrapper


# There are several possibilites of how to map a type to a Converter
# 1. The type is a subclass of the key
# 2. The type is an Alias (AliasConverter)
# 3. The type is a key
def get_converter(kind: type) -> type[BaseConverter]:
    kind = utils.unwrap_type(kind)

    if kind in converter_mapping:
        return converter_mapping[kind]

    for cls in kind.mro():
        if cls in converter_mapping:
            return converter_mapping[cls]

    raise errors.ArcError(f"No Converter found for {kind}")
