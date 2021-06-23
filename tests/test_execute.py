"""End to end testing for Commands"""
from unittest import mock
from typing import Literal
from pathlib import Path
import enum
import pytest

from arc.types import Range, ValidPath
from arc import ParsingMethod
from arc.errors import ConversionError, CommandError
from .mock import MockedCommand


def test_keybab(cli: MockedCommand):
    @cli.subcommand()
    def two_words(first_name):
        ...

    cli("two_words first_name=sean")
    cli("two-words first-name=sean")

    assert two_words.function.call_count == 2


def test_positional(cli: MockedCommand):
    @cli.subcommand(parsing_method=ParsingMethod.POSITIONAL)
    def pos(val: int):
        ...

    cli("pos 2")
    pos.function.assert_called_with(val=2)


def test_float(cli: MockedCommand):
    @cli.subcommand()
    def fl(val: float):
        ...

    cli("fl val=2.3")
    fl.function.assert_called_with(val=2.3)


def test_bytes(cli: MockedCommand):
    @cli.subcommand()
    def by(val: bytes):
        ...

    cli("by val=hi")
    by.function.assert_called_with(val=b"hi")


def test_bool(cli: MockedCommand):
    @cli.subcommand()
    def bo(val: bool):
        ...

    cli("bo val=t")
    bo.function.assert_called_with(val=True)
    cli("bo val=true")
    bo.function.assert_called_with(val=True)
    cli("bo val=false")
    bo.function.assert_called_with(val=False)
    cli("bo val=f")
    bo.function.assert_called_with(val=False)


def test_list(cli: MockedCommand):
    @cli.subcommand()
    def li(val: list):
        ...

    cli("li val=1")
    li.function.assert_called_with(val=["1"])


def test_list_alias(cli: MockedCommand):
    @cli.subcommand()
    def li(val: list[int]):
        ...

    cli("li val=1,2,3")
    li.function.assert_called_with(val=[1, 2, 3])

    with pytest.raises(CommandError):
        cli("li val=ainfe")

    # @cli.subcommand()
    # def liu(val: list[Union[int, str]]):
    #     ...

    # cli("li val=word,1")
    # li.function.assert_called_with(val=["word", 1])


def test_tuple_alias(cli: MockedCommand):
    @cli.subcommand()
    def tu(val: tuple[int]):
        ...

    cli("tu val=1")
    tu.function.assert_called_with(val=(1,))

    with pytest.raises(CommandError):
        cli("tu val=1,2")


def test_set_alias(cli: MockedCommand):
    @cli.subcommand()
    def se(val: set[int]):
        ...

    cli("se val=1")
    se.function.assert_called_with(val={1})

    with pytest.raises(CommandError):
        cli("se val=word")


def test_range(cli: MockedCommand):
    @cli.subcommand()
    def ra(val: Range[Literal[1], Literal[10]]):
        ...

    cli("ra val=2")
    ra.function.assert_called_with(val=Range(2, 1, 10))

    with pytest.raises(CommandError):
        cli("ra val=99")


def test_enum(cli: MockedCommand):
    class Color(enum.Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"

    @cli.subcommand()
    def en(color: Color):
        ...

    cli("en color=red")
    en.function.assert_called_with(color=Color.RED)

    with pytest.raises(CommandError):
        cli("en color=blue")


def test_path(cli: MockedCommand):
    @cli.subcommand()
    def pa(path: Path):
        ...

    cli("pa path=./arc")
    pa.function.assert_called_with(path=Path("./arc"))


def test_validated_path(cli: MockedCommand):
    @cli.subcommand()
    def pa(path: ValidPath):
        ...

    cli("pa path=./arc")
    pa.function.assert_called_with(path=ValidPath("./arc"))

    with pytest.raises(CommandError):
        cli("pa path=doesnotexist")
