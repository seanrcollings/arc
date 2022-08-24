import pytest
import typing as t
import arc
from arc import errors
from arc.types import validators


class TestLen:
    def test_min_only(self):
        assert validators.Len(1)("1") == "1"
        assert validators.Len(4)("1234") == "1234"

        with pytest.raises(errors.ValidationError):
            validators.Len(4)("123")

        with pytest.raises(errors.ValidationError):
            validators.Len(4)("1234555")

    def test_min_max(self):
        validator = validators.Len(1, 4)
        assert validator("1") == "1"
        assert validator("12") == "12"
        assert validator("123") == "123"
        assert validator("1234") == "1234"

        with pytest.raises(errors.ValidationError):
            validator("")

        with pytest.raises(errors.ValidationError):
            validator("1234555")


def test_greater_than():
    validator = validators.GreaterThan(10)
    assert validator(11) == 11
    assert validator(12) == 12

    with pytest.raises(errors.ValidationError):
        validator(1)

    with pytest.raises(errors.ValidationError):
        validator(10)


def test_less_than():
    validator = validators.LessThan(10)
    assert validator(1) == 1
    assert validator(9) == 9

    with pytest.raises(errors.ValidationError):
        validator(11)

    with pytest.raises(errors.ValidationError):
        validator(10)


def test_between():
    validator = validators.Between(1, 10)
    assert validator(2) == 2

    with pytest.raises(errors.ValidationError):
        validator(1)

    with pytest.raises(errors.ValidationError):
        validator(10)

    with pytest.raises(errors.ValidationError):
        validator(100)


def test_matches():
    matcher = validators.Matches(r"[A-za-z]")

    assert matcher("word") == "word"

    with pytest.raises(errors.ValidationError):
        matcher("1234")
