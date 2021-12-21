import pytest
from typing import Annotated
from arc import CLI, errors, config
from arc.types import Option, Flag
from arc.types.params import Count


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

        with pytest.raises(errors.UsageError):
            cli("key --val")

    def test_keyword_default(self, cli: CLI):
        @cli.subcommand()
        def key(*, val: int = 1):
            return val

        assert cli("key") == 1
        assert cli("key --val 2") == 2

    def test_key_missing(self, cli: CLI):
        @cli.subcommand()
        def key():
            ...

        with pytest.raises(errors.UsageError):
            cli("key --val 2")

    def test_star_kwargs(self, cli: CLI):

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def key(*kwargs):
                ...

    def test_flag(self, cli: CLI):
        @cli.subcommand()
        def fl(flag: bool):
            return flag

        assert not cli("fl")
        assert cli("fl --flag") == True

        with pytest.raises(errors.UnrecognizedArgError):
            cli("fl --flag 1")

    def test_flag_default(self, cli: CLI):
        @cli.subcommand()
        def fa(flag: bool = False):
            return flag

        @cli.subcommand()
        def tr(flag: bool = True):
            return flag

        assert not cli("fa")
        assert cli("fa --flag") == True

        assert cli("tr") == True
        assert not cli("tr --flag")

    def test_flag_consume(self, cli: CLI):
        """Flags should not consume their adjacent value"""

        @cli.subcommand()
        def test(val: int, flag: bool = Flag(short="f")):
            return val, flag

        assert cli("test 1") == (1, False)
        assert cli("test 1 --flag") == (1, True)
        assert cli("test --flag 1") == (1, True)
        assert cli("test 1 -f") == (1, True)
        assert cli("test -f 1") == (1, True)


class TestParamTypes:
    def test_name(self, cli: CLI):
        @cli.subcommand()
        def na(*, name: str = Option(name="long_name")):
            return name

        assert cli("na --long_name sean") == "sean"

        with pytest.raises(errors.UsageError):
            cli("na --name sean")

    def test_short_args(self, cli: CLI):
        @cli.subcommand()
        def ar(name: str, flag: bool = Flag(short="f")):
            return name, flag

        assert cli("ar sean --flag") == ("sean", True)
        assert cli("ar sean -f") == ("sean", True)

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def _(
                arg1: bool = Flag(short="a"),
                arg2: bool = Flag(short="a"),
            ):
                ...

        with pytest.raises(errors.ArgumentError):

            @cli.subcommand()
            def _(
                arg1: bool = Flag(short="a"),
                arg2: bool = Flag(short="a2"),
            ):
                ...

    def test_count(self, cli: CLI):
        @cli.subcommand()
        def co(verbose: int = Count(default=2, short="v")):
            return verbose

        assert cli("co") == 2
        assert cli("co --verbose") == 1
        assert cli("co --verbose --verbose") == 2
        assert cli("co -v -v -v") == 3
        assert cli("co -vvv") == 3
