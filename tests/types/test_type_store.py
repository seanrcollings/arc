import typing
import enum
from arc.types import converters
from arc.types import type_store


def test_converter_retrieve():
    converter_map = {
        str: converters.StringConverter,
        bytes: converters.BytesConverter,
        enum.Enum: converters.EnumConverter,
        typing.Literal["test1", "test2"]: converters.LiteralConverter,
        typing.Literal["test1", "ainfeianf["]: converters.LiteralConverter,
        typing.Union[str, int]: converters.UnionConverter,
    }
    for key, val in converter_map.items():
        assert type_store.get_converter(key) is val


class TestDisplayName:
    def test_basic(self):
        assert type_store.get_display_name(str) == "string"
        assert type_store.get_display_name(int) == "integer"
        assert type_store.get_display_name(list) == "list"
        assert type_store.get_display_name(bool) == "flag"

    def test_list(self):
        assert type_store.get_display_name(list[int]) == "list of integers"

    def test_tuple(self):
        assert (
            type_store.get_display_name(tuple[int, str])
            == "tuple of integer and string"
        )

    def test_set(self):
        assert type_store.get_display_name(set[int]) == "set of integers"

    def test_union(self):
        assert (
            type_store.get_display_name(list[typing.Union[int, str]])
            == "list of integer or strings"
        )

        assert (
            type_store.get_display_name(typing.Union[list[int], list[str]])
            == "list of integers or list of strings"
        )

        assert (
            type_store.get_display_name(set[typing.Union[int, str]])
            == "set of integer or strings"
        )

        assert (
            type_store.get_display_name(typing.Union[set[int], set[str]])
            == "set of integers or set of strings"
        )

        assert (
            type_store.get_display_name(typing.Union[tuple[int], tuple[str]])
            == "tuple of integer or tuple of string"
        )

    def test_enum(self):
        class Color(enum.Enum):
            RED = "red"
            YELLOW = "yellow"
            BLUE = "blue"

        assert type_store.get_display_name(Color) == "red, yellow or blue"

    def test_literal(self):
        assert (
            type_store.get_display_name(typing.Literal["test1", "test2"])
            == "test1 or test2"
        )
