import typing as t
import pytest
import arc
from arc import errors, validators


def test_matches():
    matcher = validators.Matches(r"[A-za-z]")

    assert matcher("word") == "word"

    with pytest.raises(errors.ValidationError):
        matcher("1234")
