from arc.present.joiner import Join
from arc.color import colorize, fg, bg, fx


class TestJoin:
    def test_join(self):
        assert Join.together([1, 2, 3, 4], ",") == "1,2,3,4"
        assert Join.together([1, 2, 3, 4], " ") == "1 2 3 4"

    def test_remove_falsey(self):
        assert (
            Join.together([1, 2, 3, 4, False, None, []], ",", remove_falsey=True)
            == "1,2,3,4"
        )

    def test_color(self):
        assert Join.together([1, 2, 3, 4], ",", style=fg.RED) == ",".join(
            colorize(v, fg.RED) for v in [1, 2, 3, 4]
        )


def test_with_space():
    assert Join.with_space([1, 2, 3, 4]) == "1 2 3 4"


def test_with_comman():
    assert Join.with_comma([1, 2, 3, 4]) == "1, 2, 3, 4"


def test_in_groups():
    assert Join.in_groups([1, 2], [3, 4], " ", " between ") == "1 2 between 3 4"
    assert Join.in_groups([1, 2, 3], [3, 4], " ", " between ") == "1 2 3 between 3 4"
    assert Join.in_groups([1, 2, 3], [], " ", " between ") == "1 2 3 between "


def test_with_last():
    assert Join.with_last([1, 2, 3, 4], ", ", " last ") == "1, 2, 3 last 4"
    assert Join.with_last([1], ", ", " last ") == "1"
    assert Join.with_last([], ", ", " last ") == ""


def test_with_and():
    assert Join.with_and([1, 2, 3, 4]) == "1, 2, 3 and 4"
    assert Join.with_and([1]) == "1"
    assert Join.with_and([]) == ""


def test_with_or():
    assert Join.with_or([1, 2, 3, 4]) == "1, 2, 3 or 4"
    assert Join.with_or([1]) == "1"
    assert Join.with_or([]) == ""
