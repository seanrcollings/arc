from typing import (  # type: ignore
    GenericAlias,
    Union,
    Literal,
    Any,
    get_args,
    get_origin,
    Sequence,
)

from arc import errors
from arc.types.type_store import register, type_store
from arc.types import helpers
from .base_converter import BaseConverter


class GenericConverter(BaseConverter):
    def __init__(self, annotation: GenericAlias = None):
        super().__init__(annotation)
        self.args = get_args(annotation)
        self.origin = get_origin(annotation)


def format_union(union: type[Union[Any]]) -> str:
    args = get_args(union)
    names = list(type_store.get_display_name(arg) for arg in args)
    return helpers.join_or(names)


@register(Union, format_union)
class UnionConverter(GenericConverter):
    def convert(self, value: str):
        for union_type in self.args:
            try:
                converter = type_store.get_converter(union_type)
                return converter(union_type).convert(value)
            except errors.ConversionError:
                continue

        expected = ", ".join(arg.__name__ for arg in self.args[: len(self.args) - 1])
        raise errors.ConversionError(
            value, expected=expected + f" or {self.args[-1].__name__}"
        )


@register(Literal, lambda l: helpers.join_or(get_args(l)))
class LiteralConverter(GenericConverter):
    def convert(self, value: str) -> str:
        if value in self.args:
            return value

        expected = ", ".join(arg for arg in self.args[:-1])
        raise errors.ConversionError(value, expected=expected + f" or {self.args[-1]}")


class CollectionConverter(GenericConverter):
    convert_to: type

    def convert(self, value: str):
        items = [value.strip(" ") for value in value.split(",")]
        if self.args:
            return self.generic_convert(items)
        return self.basic_convert(items)

    def basic_convert(self, items: list):
        return self.convert_to(items)

    def generic_convert(self, items: list):
        return items


class MutableCollectionConverter(CollectionConverter):
    def generic_convert(self, items: list):
        item_type = self.args[0]
        converter = type_store.get_converter(item_type)(item_type)
        return self.convert_to(converter.convert(item) for item in items)


def format_collection(collection: type[Sequence]):
    origin = get_origin(collection)
    origin_display_name = origin.__name__ if origin else collection.__name__
    args = get_args(collection)
    arg_display_name = type_store.get_display_name(args[0]) if args else None

    if arg_display_name:
        return f"{origin_display_name} of {arg_display_name}s"

    return f"{origin_display_name}"


@register(list, format_collection)
class ListConverter(MutableCollectionConverter):
    convert_to = list


@register(set, format_collection)
class SetConverter(MutableCollectionConverter):
    convert_to = set


def format_tuple(tup: type[tuple]):
    args = get_args(tup)

    if args:
        if args[-1] is Ellipsis:
            return f"tuple of {type_store.get_display_name(args[0])}s"

        names = helpers.join_and(list(type_store.get_display_name(arg) for arg in args))
        return f"tuple of {names}"
    return "tuple"


@register(tuple, format_tuple)
class TupleConverter(CollectionConverter):
    convert_to = tuple

    def generic_convert(self, items: list):
        # Handle arbitrarily sized tuples
        if len(self.args) == 2 and self.args[-1] is Ellipsis:
            item_type = self.args[0]
            converter = type_store.get_converter(item_type)(item_type)
            return tuple(converter.convert(item) for item in items)
        else:
            # Handle statically sized tuples
            if len(self.args) != len(items):
                raise errors.ConversionError(
                    items,
                    expected=f"{len(self.args)} values "
                    f"({', '.join(arg.__name__ for arg in self.args)})",
                )
            return tuple(
                type_store.get_converter(item_type)(item_type).convert(item)
                for item_type, item in zip(self.args, items)
            )
