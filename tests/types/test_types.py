from typing import Annotated, Literal, Union
from pathlib import Path
import enum
import pytest

from arc import errors
from arc.types import File, Range
from arc import CLI


def test_float(cli: CLI):
    @cli.subcommand()
    def fl(val: float):
        return val

    assert cli("fl 2.3") == 2.3


def test_bytes(cli: CLI):
    @cli.subcommand()
    def by(val: bytes):
        return val

    assert cli("by hi") == b"hi"


def test_bool(cli: CLI):
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


class TestList:
    def test_standard(self, cli: CLI):
        @cli.subcommand()
        def li(val: list):
            return val

        assert cli("li 1") == ["1"]
        assert cli("li 1,2,3,4") == ["1", "2", "3", "4"]

    def test_generic(self, cli: CLI):
        @cli.subcommand()
        def li(val: list[int]):
            return val

        assert cli("li 1,2,3") == [1, 2, 3]

        with pytest.raises(errors.ArgumentError):
            cli("li ainfe")

    def test_nested_union(self, cli: CLI):
        @cli.subcommand()
        def liu(val: list[Union[int, str]]):
            return val

        assert cli("liu word,1") == ["word", 1]


class TestTuple:
    def test_standard(self, cli: CLI):
        @cli.subcommand()
        def tu(val: tuple):
            return val

        assert cli("tu 1") == ("1",)
        assert cli("tu 1,2") == ("1", "2")

    def test_static_size(self, cli: CLI):
        @cli.subcommand()
        def tu(val: tuple[int]):
            assert val == (1,)

        cli("tu 1")

        with pytest.raises(errors.ArgumentError):
            cli("tu 1,2")

    def test_variable_size(self, cli: CLI):
        @cli.subcommand()
        def any_size(val: tuple[int, ...]):
            for i in val:
                assert isinstance(i, int)

        cli("any-size 1")
        cli("any-size 1,2,3,4")
        cli("any-size 1,2,3,4,5,6")


def test_set_generic(cli: CLI):
    @cli.subcommand()
    def se(val: set[int]):
        return val

    assert cli("se 1") == {1}

    with pytest.raises(errors.ArgumentError):
        cli("se word")


class TestDict:
    def test_standard(self, cli: CLI):
        @cli.subcommand()
        def di(val: dict):
            return val

        assert cli("di one=1,two=2,three=3") == dict(one="1", two="2", three="3")

    def test_generic(self, cli: CLI):
        @cli.subcommand()
        def di(val: dict[str, int]):
            return val

        assert cli("di one=1,two=2,three=3") == dict(one=1, two=2, three=3)

        with pytest.raises(errors.InvalidParamaterError):
            cli("di one=1,two=2,three=three")


def test_enum(cli: CLI):
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


def test_path(cli: CLI):
    @cli.subcommand()
    def pa(path: Path):
        return path

    assert cli("pa ./arc") == Path("./arc")


class TestUnion:
    def test_standard(self, cli: CLI):
        @cli.subcommand()
        def un(*, val: Union[int, str] = 2):
            return val

        assert cli("un --val 2") == 2
        assert cli("un --val string") == "string"
        assert cli("un") == 2

    def test_nested(self, cli: CLI):
        @cli.subcommand()
        def un(val: list[Union[int, str]]):
            return val

        assert cli("un 1,2,3,4") == [1, 2, 3, 4]
        assert cli("un 1,string,2,string") == [1, "string", 2, "string"]

        @cli.subcommand()
        def un2(val: Union[list[int], list[str]]):
            return val

        assert cli("un2 1,2,3,4") == [1, 2, 3, 4]
        assert cli("un2 1,string,3,4") == ["1", "string", "3", "4"]


def test_literal(cli: CLI):
    @cli.subcommand()
    def li(mode: Literal["small", "big", "medium"] = "medium"):
        return mode

    assert cli("li small") == "small"
    assert cli("li big") == "big"
    assert cli("li medium") == "medium"
    assert cli("li") == "medium"

    with pytest.raises(errors.ArgumentError):
        cli("li other")


def test_file(cli: CLI):
    @cli.command()
    def fi(file: File.Read):
        return file

    file = cli("fi .arc")
    assert file.mode == "r"
    assert file.closed


def test_range(cli: CLI):
    @cli.command()
    def ra(range: Annotated[Range, 1, 10]):
        return range

    assert (res := cli("ra 1")) == 1 and isinstance(res, Range)
    assert cli("ra 5") == 5
    assert cli("ra 10") == 10

    with pytest.raises(errors.InvalidParamaterError):
        cli("ra 11")

    with pytest.raises(errors.ArgumentError):

        @cli.command()
        def ra(range: Range):
            return int(range)

        cli("ra 10")
