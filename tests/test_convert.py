import typing as t
import pytest
import arc
from arc import errors
from arc.types import validators


class TestType:
    ...


class TestMiddleware:
    def test_matches(self):
        assert (
            arc.convert("word", t.Annotated[str, validators.Matches(r"[A-za-z]")])
            == "word"
        )

        with pytest.raises(errors.ValidationError):
            arc.convert("1234", t.Annotated[str, validators.Matches(r"[A-za-z]")])

    class TestLen:
        def test_min_only(self):
            assert arc.convert("1", t.Annotated[str, validators.Len(1)]) == "1"
            assert arc.convert("1234", t.Annotated[str, validators.Len(4)]) == "1234"

            with pytest.raises(errors.ValidationError):
                arc.convert("123", t.Annotated[str, validators.Len(4)])

            with pytest.raises(errors.ValidationError):
                arc.convert("1234555", t.Annotated[str, validators.Len(4)])

        def test_min_max(self):
            assert arc.convert("1", t.Annotated[str, validators.Len(1, 4)]) == "1"
            assert arc.convert("12", t.Annotated[str, validators.Len(1, 4)]) == "12"
            assert arc.convert("123", t.Annotated[str, validators.Len(1, 4)]) == "123"
            assert arc.convert("1234", t.Annotated[str, validators.Len(1, 4)]) == "1234"

            with pytest.raises(errors.ValidationError):
                arc.convert("", t.Annotated[str, validators.Len(1, 4)])

            with pytest.raises(errors.ValidationError):
                arc.convert("1234555", t.Annotated[str, validators.Len(1, 4)])

    def test_greater_than(self):
        assert arc.convert("11", t.Annotated[int, validators.GreaterThan(10)]) == 11
        assert arc.convert("12", t.Annotated[int, validators.GreaterThan(10)]) == 12

        with pytest.raises(errors.ValidationError):
            arc.convert("1", t.Annotated[int, validators.GreaterThan(10)])

    def test_less_than(self):
        assert arc.convert("1", t.Annotated[int, validators.LessThan(10)]) == 1

        with pytest.raises(errors.ValidationError):
            arc.convert("11", t.Annotated[int, validators.LessThan(10)])

    def test_between(self):
        assert arc.convert("2", t.Annotated[int, validators.Between(1, 10)]) == 2

        with pytest.raises(errors.ValidationError):
            arc.convert("1", t.Annotated[int, validators.Between(1, 10)])

        with pytest.raises(errors.ValidationError):
            arc.convert("10", t.Annotated[int, validators.Between(1, 10)])
