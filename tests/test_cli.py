import contextlib
import os
from pathlib import Path
import pytest

from arc import CLI, namespace, errors, Context
from arc.errors import CommandError


def test_namespace_install(cli: CLI):
    g1 = namespace("g1")
    cli.install_command(g1)
    assert g1 in cli.subcommands.values()

    g2 = namespace("g2")
    cli.install_command(g2)
    assert g2 in cli.subcommands.values()


def test_execute(cli: CLI):
    @cli.subcommand()
    def func1(x):
        return x

    @cli.subcommand()
    @cli.subcommand("func2copy")
    def func2(x: int):
        return x

    assert cli("func1 2") == "2"
    assert cli("func2 2") == 2


def test_nonexistant_command(cli: CLI):
    with pytest.raises(errors.CommandNotFound):
        cli("doesnotexist x=2")


@contextlib.contextmanager
def create_autoload_file():
    try:
        file = open("tests/autoload.py", "w")
        file.write(
            """
from arc import command

@command()
def toload():
    ...

"""
        )
        file.close()
        yield
    finally:
        os.remove("tests/autoload.py")


class TestAutoload:
    root = Path(__file__).parent.parent

    def test_autoload_file(self, cli: CLI):
        with create_autoload_file():
            cli.autoload("./tests/autoload.py")
            assert "toload" in cli.subcommands

    def test_autoload_error(self, cli: CLI):
        with create_autoload_file():
            cli.autoload("./tests/autoload.py")
            with pytest.raises(CommandError):
                cli.autoload("./tests/autoload.py")


def test_command_alias(cli: CLI):
    @cli.subcommand(("name1", "name2"))
    def name1():
        return True

    assert cli("name1")
    assert cli("name2")


class OptionCalled(Exception):
    def __init__(self, *args):
        self.args = args


class TestCLIOptions:
    def test_options(self, cli: CLI):
        @cli.options
        def options(*, flag: bool, name: str, ctx: Context):
            ctx.state.args = (flag, name)

        @cli.command()
        def command(ctx: Context):
            return ctx

        assert cli("--flag --name Sean command").state.args == (True, "Sean")

        assert cli("--name Sean command").state.args == (False, "Sean")

    def test_no_pos(self, cli: CLI):
        with pytest.raises(errors.ArgumentError):

            @cli.options
            def options(val: int):
                ...


def test_root_exectuion_only(cli: CLI):
    @cli.command()
    def command():
        command()

    with pytest.raises(errors.ArcError):
        cli("command")