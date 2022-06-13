import pytest
from arc.types import strings

# TODO: add tests for other string validators


def test_char():
    assert strings.Char("h") == "h"

    with pytest.raises(ValueError):
        strings.Char("longer")
