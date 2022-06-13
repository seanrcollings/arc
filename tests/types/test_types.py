import re
from typing import Annotated, Literal, Union, TypedDict, Any, Optional
from pathlib import Path
import enum
import pytest
import arc
from arc import errors
from arc.types import File, Range
from arc import Context


@pytest.fixture(scope="function")
def cli():
    @arc.command()
    def cli():
        ...

    return cli


def test_optional(cli: arc.Command):
    @cli.subcommand()
    def non(val: Optional[int]):
        return val

    @cli.subcommand()
    def non2(val: Optional[list[int]]):
        return val

    assert cli("non") == None
    assert cli("non 1") == 1

    assert cli("non2") == None
    assert cli("non2 1 2 3") == [1, 2, 3]


@pytest.mark.parametrize(
    "value,passing",
    [
        (1, True),
        (2, True),
        (3, True),
        (11, True),
        (99999, True),
        (100000032, True),
        ("0xFF0000", False),
        ("string", False),
    ],
)
def test_int(cli: arc.Command, value, passing: bool):
    @cli.subcommand()
    def it(val: int):
        return val

    if passing:
        assert cli(f"it {value}") == value
    else:
        with pytest.raises(errors.InvalidArgValue):
            cli(f"it {value}")


@pytest.mark.parametrize(
    "value,passing",
    [
        (1, True),
        (1121314, True),
        (1.4, True),
        (0.3, True),
        (".19", True),
        ("string", False),
    ],
)
def test_float(cli: arc.Command, value, passing: bool):
    @cli.subcommand()
    def fl(val: float):
        return val

    if passing:
        assert cli(f"fl {value}") == float(value)
    else:
        with pytest.raises(errors.InvalidArgValue):
            cli(f"fl {value}")


def test_bytes(cli: arc.Command):
    @cli.subcommand()
    def by(val: bytes):
        return val

    assert cli("by hi") == b"hi"


def test_bool(cli: arc.Command):
    @cli.subcommand()
    def true_val(val: bool):
        return val

    @cli.subcommand()
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
        @cli.subcommand()
        def li(val: list):
            return val

        assert cli("li 1") == ["1"]
        # assert cli("li 1,2,3,4") == ["1", "2", "3", "4"]
        assert cli("li 1 2 3 4") == ["1", "2", "3", "4"]

    def test_generic(self, cli: arc.Command):
        @cli.subcommand()
        def li(val: list[int]):
            return val

        assert cli("li 1 2 3") == [1, 2, 3]

        with pytest.raises(errors.ArgumentError):
            cli("li ainfe")

    def test_nested_union(self, cli: arc.Command):
        @cli.subcommand()
        def liu(val: list[Union[int, str]]):
            return val

        assert cli("liu word 1") == ["word", 1]


class TestTuple:
    def test_standard(self, cli: arc.Command):
        @cli.subcommand()
        def tu(val: tuple):
            return val

        assert cli("tu 1") == ("1",)
        assert cli("tu 1 2") == ("1", "2")

    def test_static_size(self, cli: arc.Command):
        @cli.subcommand()
        def tu(val: tuple[int]):
            return val

        assert cli("tu 1") == (1,)

        with pytest.raises(errors.UnrecognizedArgError):
            cli("tu 1 2")

    def test_static_two(self, cli: arc.Command):
        @cli.subcommand()
        def tu(val: tuple[int, int], val2: tuple[int, int]):
            return val, val2

        assert cli("tu 1 2 3 4") == ((1, 2), (3, 4))

    def test_variable_size(self, cli: arc.Command):
        @cli.subcommand()
        def any_size(val: tuple[int, ...]):
            return val

        assert cli("any-size 1") == (1,)
        assert cli("any-size 1 2 3 4") == (1, 2, 3, 4)
        assert cli("any-size 1 2 3 4 5 6") == (1, 2, 3, 4, 5, 6)


class TestSet:
    def test_standard(self, cli: arc.Command):
        ...

    def test_generic(self, cli: arc.Command):
        @cli.subcommand()
        def se(val: set[int]):
            return val

        assert cli("se 1") == {1}
        assert cli("se 1 2 3") == {1, 2, 3}
        assert cli("se 1 2 3 2 1") == {1, 2, 3}

        with pytest.raises(errors.ArgumentError):
            cli("se word")


class TestDict:
    def test_standard(self, cli: arc.Command):
        @cli.subcommand()
        def di(val: dict):
            return val

        assert cli("di one=1,two=2,three=3") == dict(one="1", two="2", three="3")

    def test_generic(self, cli: arc.Command):
        @cli.subcommand()
        def di(val: dict[str, int]):
            return val

        assert cli("di one=1,two=2,three=3") == dict(one=1, two=2, three=3)

        with pytest.raises(errors.InvalidArgValue):
            cli("di one=1,two=2,three=three")

    def test_typed_dict(self, cli: arc.Command):
        class Thing(TypedDict):
            val1: int
            val2: float

        @cli.subcommand()
        def td(val: Thing):
            return val

        assert cli("td val1=1,val2=2.0") == Thing(val1=1, val2=2.0)

        with pytest.raises(errors.InvalidArgValue):
            cli("td val1=string,val2=string")

        with pytest.raises(errors.InvalidArgValue):
            cli("td val1=string")


def test_enum(cli: arc.Command):
    class Color(enum.Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"

    @cli.subcommand()
    def en(color: Color):
        assert color == Color.RED

    cli("en red")

    with pytest.raises(errors.ArgumentError):
        cli("en blue")


def test_path(cli: arc.Command):
    @cli.subcommand()
    def pa(path: Path):
        return path

    assert cli("pa ./arc") == Path("./arc")


class TestUnion:
    def test_standard(self, cli: arc.Command):
        @cli.subcommand()
        def un(*, val: Union[int, str] = 2):
            return val

        assert cli("un --val 2") == 2
        assert cli("un --val string") == "string"
        assert cli("un") == 2

    def test_nested(self, cli: arc.Command):
        @cli.subcommand()
        def un(val: list[Union[int, str]]):
            return val

        assert cli("un 1 2 3 4") == [1, 2, 3, 4]
        assert cli("un 1 string 2 string") == [1, "string", 2, "string"]

        @cli.subcommand()
        def un2(val: Union[list[int], list[str]]):
            return val

        assert cli("un2 1,2,3,4") == [1, 2, 3, 4]
        assert cli("un2 1,string,3,4") == ["1", "string", "3", "4"]


def test_literal(cli: arc.Command):
    @cli.subcommand()
    def li(mode: Literal["small", "big", "medium"] = "medium"):
        return mode

    assert cli("li small") == "small"
    assert cli("li big") == "big"
    assert cli("li medium") == "medium"
    assert cli("li") == "medium"

    with pytest.raises(errors.ArgumentError):
        cli("li other")


def test_range(cli: arc.Command):
    @cli.subcommand()
    def ra(range: Annotated[Range, 1, 10]):
        return range

    assert (res := cli("ra 1")) == 1 and isinstance(res, Range)
    assert cli("ra 5") == 5
    assert cli("ra 10") == 10

    with pytest.raises(errors.InvalidArgValue):
        cli("ra 11")

    with pytest.raises(errors.ArgumentError):

        @cli.subcommand()
        def ra(range: Range):
            return int(range)

        cli("ra 10")


@pytest.mark.parametrize("val", ["string", 1, 2, 100000, 1.3, 200])
def test_any(cli: arc.Command, val):
    @cli.subcommand()
    def an(val: Any):
        return val

    assert cli(f"an {val}") == str(val)


def test_context(cli: arc.Command):
    @cli.subcommand()
    def ct(ctx: Context):
        return ctx

    assert isinstance(cli("ct"), Context)


def test_pattern(cli: arc.Command):
    @cli.subcommand()
    def rg(pattern: re.Pattern):
        return pattern

    assert cli("rg .+") == re.compile(".+")

    with pytest.raises(errors.ArgumentError):
        cli("rg [")
