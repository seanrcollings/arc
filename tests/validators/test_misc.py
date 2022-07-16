import typing as t
import pytest
import arc
from arc import errors, validators


def test_matches():
    assert (
        arc.convert("word", t.Annotated[str, validators.Matches(r"[A-za-z]")]) == "word"
    )

    with pytest.raises(errors.ValidationError):
        arc.convert("1234", t.Annotated[str, validators.Matches(r"[A-za-z]")])
