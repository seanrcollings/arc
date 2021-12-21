import pytest
from arc.types import strings


def test_char():
    assert strings.Char("h") == "h"

    with pytest.raises(ValueError):
        strings.Char("longer")
