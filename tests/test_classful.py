from typing import Annotated
import pytest
from arc import CLI, errors
from arc import Param, Argument, Option, Flag


def test_basic(cli: CLI):
    @cli.subcommand()
    class Test:
        val: int

        def handle(self):
            return self.val

    assert cli("Test 2") == 2

    with pytest.raises(errors.MissingArgError):
        cli("Test")


def test_default(cli: CLI):
    @cli.subcommand()
    class Test:
        val: int = 2

        def handle(self):
            return self.val

    assert cli("Test") == 2
    assert cli("Test --val 3") == 3


def test_short_args(cli: CLI):
    @cli.subcommand()
    class Test:
        val: int = Option(short="v")

        def handle(self):
            return self.val

    assert cli("Test --val 3") == 3
    assert cli("Test -v 3") == 3


def test_no_handle(cli: CLI):
    with pytest.raises(errors.CommandError):

        @cli.subcommand()
        class Test:
            ...
