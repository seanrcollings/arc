from typing import _GenericAlias as GenericAlias, Union, cast, Optional, Literal  # type: ignore

from arc import errors, utils
from .base_converter import BaseConverter
from .converter_mapping import register, get_converter


class GenericConverter(BaseConverter[GenericAlias]):
    def __init__(self, annotation: GenericAlias = None):
        super().__init__(annotation)
        if utils.is_alias(annotation):
            annotation = cast(GenericAlias, annotation)
            self.args: tuple[type, ...] = annotation.__args__
            self.origin: Optional[type] = annotation.__origin__
        else:
            self.args = tuple()
            self.origin = annotation


@register(Union)
class UnionConverter(GenericConverter):
    def convert(self, value: str):
        for union_type in self.args:
            try:
                converter = get_converter(union_type)
                return converter(union_type).convert(value)
            except errors.ConversionError:
                continue

        expected = ", ".join(arg.__name__ for arg in self.args[: len(self.args) - 1])
        raise errors.ConversionError(
            value, expected=expected + f" or {self.args[-1].__name__}"
        )


@register(Literal)
class LiteralConverter(GenericConverter):
    args: tuple[str, ...]  # type: ignore

    def convert(self, value: str) -> str:
        if value in self.args:
            return value

        expected = ", ".join(arg for arg in self.args[: len(self.args) - 1])
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
        converter = get_converter(item_type)(item_type)
        return self.convert_to(converter.convert(item) for item in items)


@register(list)
class ListConverter(MutableCollectionConverter):
    convert_to = list


@register(set)
class SetConverter(MutableCollectionConverter):
    convert_to = set


@register(tuple)
class TupleConverter(CollectionConverter):
    convert_to = tuple

    def generic_convert(self, items: list):
        # Handle arbitrarily sized tuples
        if len(self.args) == 2 and self.args[-1] is Ellipsis:
            item_type = self.args[0]
            converter = get_converter(item_type)(item_type)
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
                get_converter(item_type)(item_type).convert(item)
                for item_type, item in zip(self.args, items)
            )
