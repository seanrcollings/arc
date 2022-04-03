from contextlib import contextmanager
import pytest
from arc import autocompletions
from arc.autocompletions import completions
from arc import CLI, Param, types
import arc
from arc.params import Argument

from tests import utils


@pytest.fixture()
def ccli(cli: CLI):
    cli.subcommands.pop("debug")

    @cli.command()
    def command(arg1: types.ValidPath, *, opt1: types.File.Read, flag: bool):
        ...

    @command.subcommand()
    def sub():
        ...

    @cli.command()
    def command2():
        """command2-desc"""

    @cli.command()
    def command3():
        """command3-desc"""

    cli.name = "test"

    return cli


@pytest.fixture()
def command():
    @arc.command("test")
    def c(arg1: types.ValidPath, *, opt1: types.File.Read, flag: bool):
        ...

    return c


class TestFish:
    class TestCLI:
        def test_subcommands(self, ccli: CLI):
            ctx = ccli.create_ctx(ccli.name)

            with utils.environ(
                _TEST_COMPLETE="true",
                COMP_WORDS="cli",
                COMP_CURRENT="",
            ):
                assert completions("fish", ctx).split("\n") == [
                    "plain|command",
                    "plain|command:sub",
                    "plain|command2\tcommand2-desc",
                    "plain|command3\tcommand3-desc",
                ]

            with utils.environ(
                _TEST_COMPLETE="true",
                COMP_WORDS="cli co",
                COMP_CURRENT="co",
            ):
                assert completions("fish", ctx).split("\n") == [
                    "plain|command",
                    "plain|command:sub",
                    "plain|command2\tcommand2-desc",
                    "plain|command3\tcommand3-desc",
                ]

        @pytest.mark.parametrize("arg", ("", "a", "b", "c", "filename", "path/"))
        def test_arguments(self, ccli: CLI, arg: str):
            ctx = ccli.create_ctx(ccli.name)
            with utils.environ(
                _TEST_COMPLETE="true",
                COMP_WORDS=f"cli command {arg}",
                COMP_CURRENT=arg,
            ):
                assert completions("fish", ctx).split("\n") == [
                    f"file|{arg}",
                ]

        @pytest.mark.parametrize(
            "arg", ("-", "--", "--op", "--opt", "--h", "-h", "--f")
        )
        def test_options(self, ccli: CLI, arg: str):
            ctx = ccli.create_ctx(ccli.name)
            with utils.environ(
                _TEST_COMPLETE="true", COMP_WORDS=f"cli command {arg}", COMP_CURRENT=arg
            ):
                assert completions("fish", ctx).split("\n") == [
                    "plain|--help\tShows help documentation",
                    "plain|--flag",
                    "plain|--opt1",
                ]

        @pytest.mark.parametrize(
            "arg", ("", "file", "path/", "filename", "path/filename")
        )
        def test_option_values(self, ccli: CLI, arg: str):
            ctx = ccli.create_ctx(ccli.name)
            with utils.environ(
                _TEST_COMPLETE="true",
                COMP_WORDS=f"cli command --opt1 {arg}",
                COMP_CURRENT=arg,
            ):
                assert completions("fish", ctx).split("\n") == [
                    f"file|{arg}",
                ]

        def test_custom_completions(self, ccli: CLI):
            def _complete(info):
                return [
                    autocompletions.Completion("test1"),
                    autocompletions.Completion("test2"),
                ]

            @ccli.command()
            def custom(*, arg=Param(complete=_complete)):
                ...

            ctx = ccli.create_ctx(ccli.name)
            with utils.environ(
                _TEST_COMPLETE="true",
                COMP_WORDS=f"cli custom --arg ",
                COMP_CURRENT="",
            ):
                assert completions("fish", ctx).split("\n") == [
                    "plain|test1",
                    "plain|test2",
                ]

    class TestSingleCommand:
        @pytest.mark.parametrize("arg", ("", "a", "b", "c", "filename", "path/"))
        def test_arguments(self, command: arc.Command, arg: str):
            ctx = command.create_ctx(command.name)
            with utils.environ(
                _TEST_COMPLETE="true", COMP_WORDS=f"{arg}", COMP_CURRENT=arg
            ):
                assert completions("fish", ctx).split("\n") == [
                    f"file|{arg}",
                ]

        @pytest.mark.parametrize(
            "arg", ("-", "--", "--op", "--opt", "--h", "-h", "--f")
        )
        def test_options(self, command: arc.Command, arg: str):
            ctx = command.create_ctx(command.name)
            with utils.environ(
                _TEST_COMPLETE="true", COMP_WORDS=f"{arg}", COMP_CURRENT=arg
            ):
                assert completions("fish", ctx).split("\n") == [
                    "plain|--help\tShows help documentation",
                    "plain|--flag",
                    "plain|--opt1",
                ]

        @pytest.mark.parametrize(
            "arg", ("", "file", "path/", "filename", "path/filename")
        )
        def test_option_values(self, command: arc.Command, arg: str):
            ctx = command.create_ctx(command.name)
            with utils.environ(
                _TEST_COMPLETE="true", COMP_WORDS=f"--opt1 {arg}", COMP_CURRENT=arg
            ):
                assert completions("fish", ctx).split("\n") == [
                    f"file|{arg}",
                ]