import pytest
import arc
from arc import errors


class TestOptionDeclaration:
    def test_keyword_only(self):
        @arc.command
        def command(*, name: str):
            return name

        self.assertions(command)

    def test_param_info(self):
        @arc.command
        def command(name: str = arc.Option()):
            return name

        self.assertions(command)

    def assertions(self, command: arc.Command):
        assert command("--name Jotaro") == "Jotaro"

        with pytest.raises(errors.MissingArgValueError):
            command("")

        with pytest.raises(errors.MissingOptionValueError):
            command("--name")


def test_ordering():
    @arc.command
    def command(*, val1, val2, val3, val4):
        return val1, val2, val3, val4

    assert command("--val1 1 --val2 2 --val3 3 --val4 4") == ("1", "2", "3", "4")
    assert command("--val2 1 --val3 2 --val1 3 --val4 4") == ("3", "1", "2", "4")


def test_default():
    @arc.command
    def command(*, val="val"):
        return val

    assert command("") == "val"
    assert command("--val other-value") == "other-value"


def test_param_name():
    @arc.command
    def command(val=arc.Option(name="different-name")):
        return val

    assert command("--different-name val") == "val"


def test_short_name():
    @arc.command
    def command(val=arc.Option(short="v")):
        return val

    assert command("-v val") == "val"


@pytest.mark.parametrize("cls", [list[int], set[int], tuple[int, ...]])  # type: ignore
def test_collections(cls):
    @arc.command
    def command(*, val: cls):
        return val

    assert command("--val 1 --val 2 --val 3") == cls((1, 2, 3))
