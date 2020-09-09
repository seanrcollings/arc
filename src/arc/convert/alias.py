"""
This module defines functions to be used to convert string inputs into their
appropriate types based on the type alias provided

Union[int, str]
    - i: '1234'
    - o: 1234

    - i: 'hello'
    - o: 'hello'

List[int]
    - i: '1,2,3,4,5,6'
    - o: [1, 2, 3, 4, 5, 6]

"""

from typing import _GenericAlias as GenericAlias  # type: ignore
from typing import Union, Type

from arc.errors import ConversionError
from arc.config import Config


def is_alias(alias):
    return isinstance(alias, GenericAlias)


def convert_alias(alias: Type[GenericAlias], value: str):
    if not is_alias(alias):
        raise ConversionError(None, "Provided alias must inherit from GenericAlias")

    origin = alias.__origin__
    if origin is Union:
        return convert_union(alias, value)
    elif origin is list:
        return convert_list(alias, value)
    elif origin is set:
        return convert_set(alias, value)
    elif origin is tuple:
        return convert_tuple(alias, value)
    else:
        raise ConversionError(None, f"Type Alias for '{origin}' not supported")


def convert_union(alias, value):
    for union_type in alias.__args__:
        try:
            if is_alias(union_type):
                return convert_alias(union_type, value)

            converter = Config.get_converter(union_type.__name__)
            if converter:
                return converter().convert(value)
        except ConversionError:
            continue

    raise ConversionError(value, f"Failed to convert {alias}")


def collection_setup(collection_alias, value):
    contains_type = collection_alias.__args__[0]
    if is_alias(contains_type):
        raise ConversionError(
            contains_type, message="Arc only supports shallow Collection Type Aliases"
        )

    return value.split(","), Config.get_converter(contains_type.__name__)


def convert_list(alias, value):
    items, converter = collection_setup(alias, value)
    return list([converter().convert(item) for item in items])


def convert_set(alias, value):
    items, converter = collection_setup(alias, value)
    return set(converter().convert(item) for item in items)


def convert_tuple(alias, value):
    items, _ = collection_setup(alias, value)
    if (i_len := len(items)) != (a_len := len(alias.__args__)):
        raise ConversionError(
            value=items, message=f"{alias} expects {a_len} item(s), was {i_len}",
        )

    return tuple(
        Config.get_converter(alias.__args__[idx].__name__)().convert_wrapper(item)
        for idx, item in enumerate(items)
    )
