import pytest
import arc
from arc import errors
from arc.types import strings


def test_char():
    assert arc.convert("h", strings.Char) == "h"

    with pytest.raises(errors.ValidationError):
        arc.convert("longer", strings.Char)


def test_password():
    assert arc.convert("password", strings.Password) == strings.Password("password")
    password = arc.convert("password", strings.Password)
    assert password.data == "password"
    assert str(password) == "********"
