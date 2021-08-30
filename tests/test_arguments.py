import pytest
from arc.command.param import ParamType
from typing import Annotated
from arc import CLI, VarPositional, VarKeyword, errors, config
from arc.types import Meta


class TestSimpleSyntax:
    def test_pos(self, cli: CLI):
        @cli.subcommand()
        def pos(val: int):
            return val

        assert cli("pos 2") == 2

        with pytest.raises(errors.ArgumentError):
            cli("pos")

        with pytest.raises(errors.ArgumentError):
            cli("pos not-a-number")

    def test_default_pos(self, cli: CLI):
        @cli.subcommand()
        def pos(val: int = 1):
            return val

        assert cli("pos") == 1
        assert cli("pos 2") == 2

    def test_var_pos(self, cli: CLI):
        @cli.subcommand()
        def pos(vals: VarPositional):
            return vals

        assert cli("pos 2") == ["2"]
        assert cli("pos 1 2") == ["1", "2"]
        assert cli("pos 1 2 3") == ["1", "2", "3"]
        assert cli("pos") == []

    def test_var_pos_typed(self, cli: CLI):
        @cli.subcommand()
        def post(vals: VarPositional[int]):
            return vals

        assert cli("post 2") == [2]
        assert cli("post 1 2") == [1, 2]
        assert cli("post 1 2 3") == [1, 2, 3]
        assert cli("post") == []

    def test_star_args(self, cli: CLI):
        @cli.subcommand()
        def pos(*vals):
            ...

        with pytest.raises(errors.ArgumentError):
            cli("pos")

    def test_pos_missing(self, cli: CLI):
        @cli.subcommand()
        def pos(val):
            ...

        with pytest.raises(errors.ArgumentError):
            cli("pos val val2")

    def test_keyword(self, cli: CLI):
        @cli.subcommand()
        def key(*, val: int):
            return val

        assert cli("key --val 2") == 2

    def test_keyword_default(self, cli: CLI):
        @cli.subcommand()
        def key(*, val: int = 1):
            return val

        assert cli("key") == 1
        assert cli("key --val 2") == 2

    def test_var_keyword(self, cli: CLI):
        @cli.subcommand()
        def key(kwargs: VarKeyword):
            return kwargs

        assert cli("key") == {}
        assert cli("key --val 2 --val2 10") == {"val": "2", "val2": "10"}

    def test_var_keyword_typed(self, cli: CLI):
        @cli.subcommand()
        def key(kwargs: VarKeyword[int]):
            return kwargs

        assert cli("key") == {}
        assert cli("key --val 2 --val2 10") == {"val": 2, "val2": 10}

    def test_star_kwargs(self, cli: CLI):
        @cli.subcommand()
        def key(*kwargs):
            ...

        with pytest.raises(errors.ArgumentError):
            cli("key")

    def test_key_missing(self, cli: CLI):
        @cli.subcommand()
        def key():
            ...

        with pytest.raises(errors.MissingArgError):
            cli("key --val 2")


class TestAdvancedSyntax:
    def test_name(self, cli: CLI):
        @cli.subcommand()
        def na(name: Annotated[str, Meta(type=ParamType.KEY, name="long_name")]):
            return name

        assert cli("na --long_name sean") == "sean"

        with pytest.raises(errors.ArgumentError):
            cli("na --name sean")

    def test_short_args(self, cli: CLI):
        @cli.subcommand()
        def ar(name: str, flag: Annotated[bool, Meta(short="f")]):
            assert name == "sean"
            assert flag

        cli("ar sean --flag")
        cli("ar sean -f")

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def un(
                arg1: Annotated[bool, Meta(short="a")],
                arg2: Annotated[bool, Meta(short="a")],
            ):
                ...

            cli("un -a")

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def un(
                arg1: Annotated[bool, Meta(short="a")],
                arg2: Annotated[bool, Meta(short="a2")],
            ):
                ...

            cli("un -a")

    def test_basic_hook(self, cli: CLI):
        increment = lambda val, _param, _state: val + 1

        @cli.subcommand()
        def command(val: Annotated[int, Meta(hooks=[increment])] = 1):
            return val

        assert cli("command") == 2
        assert cli("command 2") == 3


class TestKebab:
    def test_transform(self, cli: CLI):
        @cli.subcommand()
        def two_words(*, first_name: str = "", other_arg: str = ""):
            return first_name

        assert cli("two-words --first-name sean") == "sean"
        assert cli("two-words --first-name sean --other-arg hi") == "sean"

        with pytest.raises(errors.CommandError):
            cli("two_words")

        with pytest.raises(errors.ArgumentError):
            cli("two-words --first_name sean")

    def test_disable_transform(self, cli: CLI):
        config.tranform_snake_case = False

        @cli.subcommand()
        def two_words(*, first_name: str = "", other_arg: str = ""):
            return first_name

        assert cli("two_words --first_name sean") == "sean"
        assert cli("two_words --first_name sean --other_arg hi") == "sean"

        with pytest.raises(errors.CommandError):
            cli("two-words")

        with pytest.raises(errors.ArgumentError):
            cli("two_words --first-name sean --other-arg hi")

        config.tranform_snake_case = True

    def test_explicit_name(self, cli: CLI):
        @cli.subcommand()
        def two_words(
            *,
            first_name: str = "",
            other_arg: Annotated[str, Meta(name="other_arg")] = ""
        ):
            return other_arg

        assert cli("two-words --other_arg thing") == "thing"

        with pytest.raises(errors.ArgumentError):
            assert cli("two-words --other-arg thing") == "thing"
