from typing import Literal, Union
from pathlib import Path
import enum
import pytest

from arc.errors import ArgumentError
from arc import CLI


class TestTypes:
    def test_float(self, cli: CLI):
        @cli.subcommand()
        def fl(val: float):
            return val

        assert cli("fl 2.3") == 2.3

    def test_bytes(self, cli: CLI):
        @cli.subcommand()
        def by(val: bytes):
            assert val == b"hi"

        cli("by hi")

    def test_bool(self, cli: CLI):
        @cli.subcommand()
        def true_val(val: bool):
            assert val

        @cli.subcommand()
        def false_val(val: bool = True):
            assert not val

        cli("true-val --val")

        cli("false-val --val")

    def test_list(self, cli: CLI):
        @cli.subcommand()
        def li(val: list):
            assert val == ["1"]

        cli("li 1")

    def test_list_generic(self, cli: CLI):
        @cli.subcommand()
        def li(val: list[int]):
            return val

        assert cli("li 1,2,3") == [1, 2, 3]

        with pytest.raises(ArgumentError):
            cli("li ainfe")

        @cli.subcommand()
        def liu(val: list[Union[int, str]]):
            return val

        assert cli("liu word,1") == ["word", 1]

    def test_tuple_generic(self, cli: CLI):
        @cli.subcommand()
        def tu(val: tuple[int]):
            assert val == (1,)

        cli("tu 1")

        with pytest.raises(ArgumentError):
            cli("tu 1,2")

        @cli.subcommand()
        def any_size(val: tuple[int, ...]):
            for i in val:
                assert isinstance(i, int)

        cli("any-size 1")
        cli("any-size 1,2,3,4")
        cli("any-size 1,2,3,4,5,6")

    def test_set_generic(self, cli: CLI):
        @cli.subcommand()
        def se(val: set[int]):
            assert val == {1}

        cli("se 1")

        with pytest.raises(ArgumentError):
            cli("se word")

    def test_enum(self, cli: CLI):
        class Color(enum.Enum):
            RED = "red"
            YELLOW = "yellow"
            GREEN = "green"

        @cli.subcommand()
        def en(color: Color):
            assert color == Color.RED

        cli("en red")

        with pytest.raises(ArgumentError):
            cli("en blue")

    def test_path(self, cli: CLI):
        @cli.subcommand()
        def pa(path: Path):
            assert path == Path("./arc")

        cli("pa ./arc")

    def test_union(self, cli: CLI):
        @cli.subcommand()
        def un(*, val: Union[int, str] = 2):
            return val

        assert cli("un --val 2") == 2
        assert cli("un --val string") == "string"
        assert cli("un") == 2

    def test_nested_union(self, cli: CLI):
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

    def test_literal(self, cli: CLI):
        @cli.subcommand()
        def li(mode: Literal["small", "big", "medium"] = "medium"):
            return mode

        assert cli("li small") == "small"
        assert cli("li big") == "big"
        assert cli("li medium") == "medium"
        assert cli("li") == "medium"

        with pytest.raises(ArgumentError):
            cli("li other")
