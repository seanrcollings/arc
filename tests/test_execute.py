"""End to end testing for Commands"""
from unittest import mock
from typing import Literal, Union
from pathlib import Path
import enum
import pytest

from arc.types import Range, ValidPath
from arc import ParsingMethod
from arc.errors import ConversionError, CommandError
from arc import CLI


def test_keybab(cli: CLI):
    @cli.subcommand()
    def two_words(first_name):
        assert first_name == "sean"

    cli("two_words first_name=sean")
    cli("two-words first-name=sean")


def test_positional(cli: CLI):
    @cli.subcommand(parsing_method=ParsingMethod.POSITIONAL)
    def pos(val: int):
        assert val == 2

    cli("pos 2")


def test_float(cli: CLI):
    @cli.subcommand()
    def fl(val: float):
        assert val == 2.3

    cli("fl val=2.3")


def test_bytes(cli: CLI):
    @cli.subcommand()
    def by(val: bytes):
        assert val == b"hi"

    cli("by val=hi")


def test_bool(cli: CLI):
    @cli.subcommand()
    def true_val(val: bool):
        assert val

    @cli.subcommand()
    def false_val(val: bool):
        assert not val

    cli("true-val val=t")
    cli("true-val val=true")

    cli("false-val val=false")
    cli("false-val val=f")


def test_list(cli: CLI):
    @cli.subcommand()
    def li(val: list):
        assert val == ["1"]

    cli("li val=1")


def test_list_alias(cli: CLI):
    @cli.subcommand()
    def li(val: list[int]):
        assert val == [1, 2, 3]

    cli("li val=1,2,3")

    with pytest.raises(CommandError):
        cli("li val=ainfe")

    @cli.subcommand()
    def liu(val: list[Union[int, str]]):
        assert val == ["word", 1]

    cli("liu val=word,1")


def test_tuple_alias(cli: CLI):
    @cli.subcommand()
    def tu(val: tuple[int]):
        assert val == (1,)

    cli("tu val=1")

    with pytest.raises(CommandError):
        cli("tu val=1,2")

    @cli.subcommand()
    def any_size(val: tuple[int, ...]):
        for i in val:
            assert isinstance(i, int)

    cli("any-size val=1")
    cli("any-size val=1,2,3,4")
    cli("any-size val=1,2,3,4,5,6")


def test_set_alias(cli: CLI):
    @cli.subcommand()
    def se(val: set[int]):
        assert val == {1}

    cli("se val=1")

    with pytest.raises(CommandError):
        cli("se val=word")


def test_range(cli: CLI):
    @cli.subcommand()
    def ra(val: Range[Literal[1], Literal[10]]):
        assert val == Range(2, 1, 10)

    cli("ra val=2")

    with pytest.raises(CommandError):
        cli("ra val=99")


def test_enum(cli: CLI):
    class Color(enum.Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"

    @cli.subcommand()
    def en(color: Color):
        assert color == Color.RED

    cli("en color=red")

    with pytest.raises(CommandError):
        cli("en color=blue")


def test_path(cli: CLI):
    @cli.subcommand()
    def pa(path: Path):
        assert path == Path("./arc")

    cli("pa path=./arc")


def test_validated_path(cli: CLI):
    @cli.subcommand()
    def pa(path: ValidPath):
        assert path == ValidPath("./arc")

    cli("pa path=./arc")

    with pytest.raises(CommandError):
        cli("pa path=doesnotexist")


def test_union(cli: CLI):
    @cli.subcommand()
    def un(val: Union[int, str]):
        ...

    cli("un val=2")
    cli("un val=string")


def test_nested_union(cli: CLI):
    @cli.subcommand()
    def un(val: list[Union[int, str]]):
        return val

    assert cli("un val=1,2,3,4") == [1, 2, 3, 4]
    assert cli("un val=1,string,2,string") == [1, "string", 2, "string"]

    @cli.subcommand()
    def un2(val: Union[list[int], list[str]]):
        return val

    assert cli("un2 val=1,2,3,4") == [1, 2, 3, 4]
    assert cli("un2 val=1,string,3,4") == ["1", "string", "3", "4"]


def test_arg_alias(cli: CLI):
    @cli.subcommand(arg_aliases={"name": "na", "flag": ("f", "fl")})
    def ar(name: str, flag: bool):
        assert name == "sean"
        assert flag

    cli("ar name=sean --flag")
    cli("ar na=sean -f")
    cli("ar na=sean -fl")

    with pytest.raises(CommandError):

        @cli.subcommand(arg_aliases={"arg1": "arg", "arg2": ("arg", "2")})
        def un(arg1: str, arg2: str):
            ...
