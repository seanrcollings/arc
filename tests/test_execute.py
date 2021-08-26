"""End to end testing for Commands"""
from arc.command.param import Meta
from typing import Annotated
import pytest

from arc.errors import ArgumentError, CommandError
from arc import CLI, config


class TestKebab:
    def test_transform(self, cli: CLI):
        @cli.subcommand()
        def two_words(first_name: str = "", other_arg: str = ""):
            return first_name

        assert cli("two-words --first-name sean") == "sean"
        assert cli("two-words --first-name sean --other-arg hi") == "sean"

        with pytest.raises(CommandError):
            cli("two_words")

        with pytest.raises(ArgumentError):
            cli("two-words --first_name sean")

    def test_disable_transform(self, cli: CLI):
        config.tranform_snake_case = False

        @cli.subcommand()
        def two_words(first_name: str = "", other_arg: str = ""):
            return first_name

        assert cli("two_words --first_name sean") == "sean"
        assert cli("two_words --first_name sean --other_arg hi") == "sean"

        with pytest.raises(CommandError):
            cli("two-words")

        with pytest.raises(ArgumentError):
            cli("two_words --first-name sean --other-arg hi")

        config.tranform_snake_case = True

    def test_explicit_name(self, cli: CLI):
        @cli.subcommand()
        def two_words(
            first_name: str = "", other_arg: Annotated[str, Meta(name="other_arg")] = ""
        ):
            return other_arg

        assert cli("two-words --other_arg thing") == "thing"

        with pytest.raises(ArgumentError):
            assert cli("two-words --other-arg thing") == "thing"


def test_short_args(cli: CLI):
    @cli.subcommand()
    def ar(name: str, flag: Annotated[bool, Meta(short="f")]):
        assert name == "sean"
        assert flag

    cli("ar sean --flag")
    cli("ar sean -f")

    with pytest.raises(ArgumentError):

        @cli.subcommand()
        def un(
            arg1: Annotated[bool, Meta(short="a")],
            arg2: Annotated[bool, Meta(short="a")],
        ):
            ...

        cli("un -a")

    with pytest.raises(ArgumentError):

        @cli.subcommand()
        def un(
            arg1: Annotated[bool, Meta(short="a")],
            arg2: Annotated[bool, Meta(short="a2")],
        ):
            ...

        cli("un -a")
