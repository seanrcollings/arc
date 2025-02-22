from typing import Annotated
import pytest
import arc
from arc import errors


Type = Annotated[int, arc.Argument(default=2)]

class TestArgumentDeclartion:
    def test_postional(self):
        @arc.command
        def command(name):
            return name

        assert command("Jotaro") == "Jotaro"

        with pytest.raises(errors.MissingArgValueError):
            command("")

    def test_param_info(self):
        @arc.command
        def command(name: str = arc.Argument()):
            return name

        assert command("Jotaro") == "Jotaro"

        with pytest.raises(errors.MissingArgValueError):
            command("")

    def test_in_type(self):

        @arc.command
        def command(val: Type):
            return val

        assert command("1") == 1
        assert command("") == 2

        with pytest.raises(errors.InvalidParamValueError):
            command("val")


def test_missing():
    @arc.command
    def command(val: list):
        return val

    assert command("1 2") == ["1", "2"]

    with pytest.raises(errors.MissingArgValueError):
        command("")


def test_ordering():
    @arc.command
    def command(val1, val2, val3, val4):
        return val1, val2, val3, val4

    assert command("1 2 3 4") == ("1", "2", "3", "4")


def test_default():
    @arc.command
    def command(val="val"):
        return val

    assert command("") == "val"
    assert command("other-value") == "other-value"


def test_param_name():
    @arc.command
    def command(val=arc.Argument(name="different-name")):
        return val

    assert command("val") == "val"


def test_collections():
    @arc.command
    def command(val: tuple[int, int], val2: list[int]):
        return val, val2

    assert command("1 2 3 4 5 6 7 8 9 10") == ((1, 2), [3, 4, 5, 6, 7, 8, 9, 10])
