from arc.present.joiner import Joiner
from arc.color import colorize, fg, bg, fx


class TestJoin:
    def test_join(self):
        assert Joiner.join([1, 2, 3, 4], ",") == "1,2,3,4"
        assert Joiner.join([1, 2, 3, 4], " ") == "1 2 3 4"

    def test_remove_falsey(self):
        assert (
            Joiner.join([1, 2, 3, 4, False, None, []], ",", remove_falsey=True)
            == "1,2,3,4"
        )

    def test_color(self):
        assert Joiner.join([1, 2, 3, 4], ",", style=fg.RED) == ",".join(
            colorize(v, fg.RED) for v in [1, 2, 3, 4]
        )


def test_with_space():
    assert Joiner.with_space([1, 2, 3, 4]) == "1 2 3 4"


def test_with_comman():
    assert Joiner.with_comma([1, 2, 3, 4]) == "1, 2, 3, 4"


def test_in_groups():
    assert Joiner.in_groups([1, 2], [3, 4], " ", " between ") == "1 2 between 3 4"
    assert Joiner.in_groups([1, 2, 3], [3, 4], " ", " between ") == "1 2 3 between 3 4"
    assert Joiner.in_groups([1, 2, 3], [], " ", " between ") == "1 2 3 between "


def test_with_last():
    assert Joiner.with_last([1, 2, 3, 4], ", ", " last ") == "1, 2, 3 last 4"
    assert Joiner.with_last([1], ", ", " last ") == "1"
    assert Joiner.with_last([], ", ", " last ") == ""


def test_with_and():
    assert Joiner.with_and([1, 2, 3, 4]) == "1, 2, 3 and 4"
    assert Joiner.with_and([1]) == "1"
    assert Joiner.with_and([]) == ""


def test_with_or():
    assert Joiner.with_or([1, 2, 3, 4]) == "1, 2, 3 or 4"
    assert Joiner.with_or([1]) == "1"
    assert Joiner.with_or([]) == ""
