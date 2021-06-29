from typing import _SpecialForm as SpecialForm, Union
from arc import utils, errors

from .base_converter import BaseConverter

converter_mapping: dict[Union[type, SpecialForm], type[BaseConverter]] = {}


def register(*kinds: Union[type, SpecialForm]):
    """Registers decorated `cls` as the converter for `kind`"""

    def wrapper(cls: type[BaseConverter]) -> type[BaseConverter]:
        for kind in kinds:
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
