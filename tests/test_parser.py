import pytest
import arc
from arc import errors


class TestOptionSyntax:
    def test_flag(self):
        @arc.command()
        def command(flag: bool):
            return flag

        assert not command()
        assert command("--flag")

    def test_short_flag(self):
        @arc.command()
        def command(flag: bool = arc.Flag(short="f")):
            return flag

        assert not command()
        assert command("-f")

    def test_unique_prefix(self):
        @arc.command()
        def command(flag: bool):
            return flag

        assert not command()

        for string in ["--f", "--fl", "--fla", "--flag"]:
            assert command(string)

        with pytest.raises(errors.ArgumentError):
            command("-f")

    def test_value_with_space(self):
        @arc.command()
        def command(*, value: int):
            return value

        assert command("--value 42") == 42

    def test_value_with_equal(self):
        @arc.command()
        def command(*, value: int):
            return value

        assert command("--value=42") == 42
        assert command("--v=42") == 42
