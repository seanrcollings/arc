from typing import _GenericAlias, Union, List, Set, Tuple, Type
from arc.config import Config
from arc.errors import ConversionError


def get_converter(obj):
    converter = Config.converters.get(obj.__name__)
    if converter is None:
        raise KeyError("Converter not found")
    return converter


def convert_alias(alias: Type[_GenericAlias], value: str):
    if not isinstance(alias, _GenericAlias):
        raise RuntimeError("Provided alias must inherit from _GenericAlias")

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
        print(origin)


def convert_union(alias, value):
    for union_type in alias.__args__:
        try:
            if isinstance(union_type, _GenericAlias):
                return convert_alias(union_type, value)

            converter = get_converter(union_type)
            if converter:
                return converter().convert(value)
        except ConversionError:
            continue

    raise ConversionError(value, f"Failed to convert {alias}")


def collection_setup(collection_alias, value):
    if "," not in value:
        raise ConversionError(value)

    items = [item.strip() for item in value.split(",")]
    _type = collection_alias.__args__[0]
    converter = get_converter(_type)()

    return items, converter


def convert_list(alias, value):
    items, converter = collection_setup(alias, value)
    return list([converter.convert(item) for item in items])


def convert_set(alias, value):
    items, converter = collection_setup(alias, value)
    return set({converter.convert(item) for item in items})


def convert_tuple(alias, value):
    items, converter = collection_setup(alias, value)
    return tuple(converter.convert(item) for item in items)


converted = convert_alias(Union[Union[List[int], int], Union[str, int]], "1,2,3,4")
print(type(converted), "|", converted)
