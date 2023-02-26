from typing import Annotated
import pytest
import arc
from arc import errors


class TestFlagDeclaration:
    def test_annotation(self):
        @arc.command
        def command(flag: bool):
            return flag

        assert not command("")
        assert command("--flag")

    def test_default_value(self):
        @arc.command
        def command(flag=False):
            return flag

        assert not command("")
        assert command("--flag")

    def test_param_info(self):
        @arc.command
        def command(flag=arc.Flag()):
            return flag

        assert not command("")
        assert command("--flag")


def test_ordering():
    @arc.command
    def command(val1: bool, val2: bool, val3: bool, val4: bool):
        return val1, val2, val3, val4

    assert command("--val1 --val2 --val3 --val4") == (True, True, True, True)
    assert command("--val1 --val3 ") == (True, False, True, False)


def test_default():
    @arc.command
    def command(val: bool = True):
        return val

    assert command("")
    assert not command("--val")


def test_param_name():
    @arc.command
    def command(val=arc.Flag(name="different-name")):
        return val

    assert command("--different-name")


def test_short_name():
    @arc.command
    def command(val=arc.Flag(short="v")):
        return val

    assert command("-v")


def test_annotation():
    @arc.command
    def command(val: Annotated[bool, 1]):
        return val

    assert command("") == False
    assert command("--val")
