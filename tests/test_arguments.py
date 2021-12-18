import pytest
from typing import Annotated
from arc import CLI, errors, config
from arc.types import VarPositional, VarKeyword, Param, PosParam, KeyParam, FlagParam


class TestSimpleSyntax:
    def test_pos(self, cli: CLI):
        @cli.subcommand()
        def pos(val: int):
            return val

        assert cli("pos 2") == 2

        with pytest.raises(errors.UsageError):
            cli("pos")

        with pytest.raises(errors.ArgumentError):
            cli("pos not-a-number")

    def test_default_pos(self, cli: CLI):
        @cli.subcommand()
        def pos(val: int = 1):
            return val

        assert cli("pos") == 1
        assert cli("pos 2") == 2

    # def test_var_pos(self, cli: CLI):
    #     @cli.subcommand()
    #     def pos(vals: VarPositional):
    #         return vals

    #     assert cli("pos 2") == ["2"]
    #     assert cli("pos 1 2") == ["1", "2"]
    #     assert cli("pos 1 2 3") == ["1", "2", "3"]
    #     assert cli("pos") == []

    # def test_var_pos_typed(self, cli: CLI):
    #     @cli.subcommand()
    #     def post(vals: VarPositional[int]):
    #         return vals

    #     assert cli("post 2") == [2]
    #     assert cli("post 1 2") == [1, 2]
    #     assert cli("post 1 2 3") == [1, 2, 3]
    #     assert cli("post") == []

    def test_star_args(self, cli: CLI):

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def pos(*vals):
                ...

    def test_pos_missing(self, cli: CLI):
        @cli.subcommand()
        def pos(val):
            ...

        with pytest.raises(errors.UsageError) as excinfo:
            cli("pos val val2")

        assert "Too many positional arguments" in str(excinfo.value)

    def test_keyword(self, cli: CLI):
        @cli.subcommand()
        def key(*, val: int):
            return val

        assert cli("key --val 2") == 2

        with pytest.raises(errors.UsageError):
            cli("key")

    def test_keyword_default(self, cli: CLI):
        @cli.subcommand()
        def key(*, val: int = 1):
            return val

        assert cli("key") == 1
        assert cli("key --val 2") == 2

    # def test_var_keyword(self, cli: CLI):
    #     @cli.subcommand()
    #     def key(kwargs: VarKeyword):
    #         return kwargs

    #     assert cli("key") == {}
    #     assert cli("key --val 2 --val2 10") == {"val": "2", "val2": "10"}

    # def test_var_keyword_typed(self, cli: CLI):
    #     @cli.subcommand()
    #     def key(kwargs: VarKeyword[int]):
    #         return kwargs

    #     assert cli("key") == {}
    #     assert cli("key --val 2 --val2 10") == {"val": 2, "val2": 10}

    def test_star_kwargs(self, cli: CLI):

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def key(*kwargs):
                ...

    def test_key_missing(self, cli: CLI):
        @cli.subcommand()
        def key():
            ...

        with pytest.raises(errors.UsageError):
            cli("key --val 2")


class TestParamSyntax:
    def test_name(self, cli: CLI):
        @cli.subcommand()
        def na(*, name: str = KeyParam(name="long_name")):
            return name

        assert cli("na --long_name sean") == "sean"

        with pytest.raises(errors.UsageError):
            cli("na --name sean")

    def test_short_args(self, cli: CLI):
        @cli.subcommand()
        def ar(name: str, flag: bool = FlagParam(short="f")):
            return name, flag

        assert cli("ar sean --flag") == ("sean", True)
        assert cli("ar sean -f") == ("sean", True)

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def un(
                arg1: bool = FlagParam(short="a"),
                arg2: bool = FlagParam(short="a"),
            ):
                ...

            cli("un -a")

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def un(
                arg1: bool = FlagParam(short="a"),
                arg2: bool = FlagParam(short="a2"),
            ):
                ...

            cli("un -a")


class TestKebab:
    def test_transform(self, cli: CLI):
        @cli.subcommand()
        def two_words(*, first_name: str = "", other_arg: str = ""):
            return first_name

        assert cli("two-words --first-name sean") == "sean"
        assert cli("two-words --first-name sean --other-arg hi") == "sean"

        with pytest.raises(errors.Exit):
            cli("two_words")

        with pytest.raises(errors.UsageError):
            cli("two-words --first_name sean")

    def test_disable_transform(self, cli: CLI):
        try:
            config.transform_snake_case = False

            @cli.subcommand()
            def two_words(*, first_name: str = "", other_arg: str = ""):
                return first_name

            assert cli("two_words --first_name sean") == "sean"
            assert cli("two_words --first_name sean --other_arg hi") == "sean"

            with pytest.raises(errors.Exit):
                cli("two-words")

            with pytest.raises(errors.UsageError):
                cli("two_words --first-name sean --other-arg hi")
        finally:
            config.transform_snake_case = True
