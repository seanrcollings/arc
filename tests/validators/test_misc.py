import typing as t
import pytest
from arc import errors
from arc.types import validators


def test_matches():
    matcher = validators.Matches(r"[A-za-z]")

    assert matcher("word") == "word"

    with pytest.raises(errors.ValidationError):
        matcher("1234")
