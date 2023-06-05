import datetime
import re
from typing import Literal, Union, TypedDict, Any, Optional
import uuid
from hypothesis import given, example, infer, strategies as st
from pathlib import Path
import enum
import pytest

import arc
from arc import errors


@pytest.fixture(scope="function")
def cli():
    return arc.namespace("cli")


def textarguments():
    return st.text(
        st.characters(
            blacklist_categories=["Nd"], blacklist_characters=["-", "'", '"']
        ),
        min_size=1,
    )


class TestNone:
    def test_optional(self, cli: arc.Command):
        @cli.subcommand
        def non(val: Optional[int]):
            return val

        assert cli("non") == None
        assert cli("non 1") == 1

    def test_none(self, cli: arc.Command):
        @cli.subcommand
        def non(val: int | None):
            return val

        assert cli("non") == None
        assert cli("non 1") == 1


class TestInt:
    @given(value=infer)
    @example(999999)
    @example(10000000000032)
    def test_succeed(self, value: int):
        @arc.command
        def it(val: int):
            return val

        assert it(f"{value}") == value

    @given(value=textarguments())
    @example("0xFF000")
    def test_failure(self, value: str):
        @arc.command
        def it(val: int):
            return val

        with pytest.raises(errors.InvalidParamValueError):
            it(f"{value!r}")


class TestFloat:
    @given(st.floats(min_value=0))
    def test_succeed(self, value: float):
        @arc.command
        def fl(val: float):
            return val

        assert fl(str(value)) == value

    @given(value=textarguments())
    def test_failure(self, value: str):
        @arc.command
        def fl(val: float):
            return val

        with pytest.raises(errors.InvalidParamValueError):
            assert fl(f"{value!r}")


def test_bytes(cli: arc.Command):
    @cli.subcommand
    def by(val: bytes):
        return val

    assert cli("by hi") == b"hi"


def test_bool(cli: arc.Command):
    @cli.subcommand
    def true_val(val: bool):
        return val

    @cli.subcommand
    def false_val(val: bool = True):
        return val

    assert not cli("true-val")
    assert cli("true-val --val")
    assert cli("false-val")
    assert not cli("false-val --val")

    with pytest.raises(errors.UnrecognizedArgError):
        cli("true-val --val 2")


class TestList:
    def test_standard(self, cli: arc.Command):
        @cli.subcommand
        def li(val: list):
            return val

        assert cli("li 1") == ["1"]
        # assert cli("li 1,2,3,4") == ["1", "2", "3", "4"]
        assert cli("li 1 2 3 4") == ["1", "2", "3", "4"]

    def test_generic(self, cli: arc.Command):
        @cli.subcommand
        def li(val: list[int]):
            return val

        assert cli("li 1 2 3") == [1, 2, 3]

        with pytest.raises(errors.ArgumentError):
            cli("li ainfe")

    def test_nested_union(self, cli: arc.Command):
        @cli.subcommand
        def liu(val: list[Union[int, str]]):
            return val

        assert cli("liu word 1") == ["word", 1]

    def test_append(self, cli: arc.Command):
        @cli.subcommand
        def li(*, val: list):
            return val

        assert cli("li --val 1") == ["1"]
        # assert cli("li 1,2,3,4") == ["1", "2", "3", "4"]
        assert cli("li --val 1 --val 2 --val 3 --val 4") == ["1", "2", "3", "4"]


class TestTuple:
    def test_standard(self, cli: arc.Command):
        @cli.subcommand
        def tu(val: tuple):
            return val

        assert cli("tu 1") == ("1",)
        assert cli("tu 1 2") == ("1", "2")

    def test_static_size(self, cli: arc.Command):
        @cli.subcommand
        def tu(val: tuple[int]):
            return val

        assert cli("tu 1") == (1,)

        with pytest.raises(errors.UnrecognizedArgError):
            cli("tu 1 2")

    def test_static_two(self, cli: arc.Command):
        @cli.subcommand
        def tu(val: tuple[int, int], val2: tuple[int, int]):
            return val, val2

        assert cli("tu 1 2 3 4") == ((1, 2), (3, 4))

    def test_variable_size(self, cli: arc.Command):
        @cli.subcommand
        def any_size(val: tuple[int, ...]):
            return val

        assert cli("any-size 1") == (1,)
        assert cli("any-size 1 2 3 4") == (1, 2, 3, 4)
        assert cli("any-size 1 2 3 4 5 6") == (1, 2, 3, 4, 5, 6)

    def test_not_enough_args(self, cli: arc.Command):
        @cli.subcommand
        def not_enough_pos(val: tuple[int, int]):
            return val

        with pytest.raises(errors.ParserError):
            cli("not-enough-pos 1")

        @cli.subcommand
        def not_enough_opt(*, val: tuple[int, int]):
            return val

        with pytest.raises(errors.InvalidParamValueError):
            cli("not-enough-opt --val 1")


class TestSet:
    def test_standard(self, cli: arc.Command):
        ...

    def test_generic(self, cli: arc.Command):
        @cli.subcommand
        def se(val: set[int]):
            return val

        assert cli("se 1") == {1}
        assert cli("se 1 2 3") == {1, 2, 3}
        assert cli("se 1 2 3 2 1") == {1, 2, 3}

        with pytest.raises(errors.ArgumentError):
            cli("se word")


class TestDict:
    def test_standard(self, cli: arc.Command):
        @cli.subcommand
        def di(val: dict):
            return val

        assert cli("di one=1,two=2,three=3") == dict(one="1", two="2", three="3")

    def test_generic(self, cli: arc.Command):
        @cli.subcommand
        def di(val: dict[str, int]):
            return val

        assert cli("di one=1,two=2,three=3") == dict(one=1, two=2, three=3)

        with pytest.raises(errors.InvalidParamValueError):
            cli("di one=1,two=2,three=three")

    def test_typed_dict(self, cli: arc.Command):
        class Thing(TypedDict):
            val1: int
            val2: float

        @cli.subcommand
        def td(val: Thing):
            return val

        assert cli("td val1=1,val2=2.0") == Thing(val1=1, val2=2.0)

        with pytest.raises(errors.InvalidParamValueError):
            cli("td val1=string,val2=string")

        with pytest.raises(errors.InvalidParamValueError):
            cli("td val1=string")


def test_enum(cli: arc.Command):
    class Color(enum.Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"

    @cli.subcommand
    def en(color: Color):
        assert color == Color.RED

    cli("en red")

    with pytest.raises(errors.ArgumentError):
        cli("en blue")


def test_path(cli: arc.Command):
    @cli.subcommand
    def pa(path: Path):
        return path

    assert cli("pa ./arc") == Path("./arc")


class TestUnion:
    def test_standard(self, cli: arc.Command):
        @cli.subcommand
        def un(*, val: Union[int, str] = 2):
            return val

        assert cli("un --val 2") == 2
        assert cli("un --val string") == "string"
        assert cli("un") == 2

    def test_nested(self, cli: arc.Command):
        @cli.subcommand
        def un(val: list[Union[int, str]]):
            return val

        assert cli("un 1 2 3 4") == [1, 2, 3, 4]
        assert cli("un 1 string 2 string") == [1, "string", 2, "string"]

    def test_collections_not_allowed(self, cli):
        @cli.subcommand
        def un2(val: Union[list[int], list[str]]):
            return val

        with pytest.raises(errors.ParamError):
            cli()

    def test_310_type(self, cli: arc.Command):
        @cli.subcommand
        def un(val: float | int):
            return val

        assert cli("un 2") == 2
        assert cli("un 2.0") == 2.0


def test_literal(cli: arc.Command):
    @cli.subcommand
    def li(mode: Literal["small", "big", "medium"] = "medium"):
        return mode

    assert cli("li small") == "small"
    assert cli("li big") == "big"
    assert cli("li medium") == "medium"
    assert cli("li") == "medium"

    with pytest.raises(errors.ArgumentError):
        cli("li other")


@pytest.mark.parametrize("val", ["string", 1, 2, 100000, 1.3, 200])
def test_any(cli: arc.Command, val):
    @cli.subcommand
    def an(val: Any):
        return val

    assert cli(f"an {val}") == str(val)


def test_pattern(cli: arc.Command):
    @cli.subcommand
    def rg(pattern: re.Pattern):
        return pattern

    assert cli("rg .+") == re.compile(".+")

    with pytest.raises(errors.ArgumentError):
        cli("rg [")


def test_uuid(cli: arc.Command):
    @cli.subcommand
    def ui(val: uuid.UUID):
        return val

    assert cli("ui 123e4567-e89b-12d3-a456-426614174000") == uuid.UUID(
        "123e4567-e89b-12d3-a456-426614174000"
    )

    with pytest.raises(errors.ArgumentError):
        cli("ui bad")


