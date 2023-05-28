import pytest
import arc
from arc.types import numbers
from arc import errors

INTS = [
    (numbers.Binary, "11", 3),
    (numbers.Binary, "1111101010101", 8021),
    (numbers.Binary, "2", None),
    (numbers.Binary, "string", None),
    (numbers.Oct, "10", 8),
    (numbers.Oct, "7", 7),
    (numbers.Oct, "8", None),
    (numbers.Oct, "99", None),
    (numbers.Oct, "fff", None),
    (numbers.Hex, "1", 1),
    (numbers.Hex, "fff", 4095),
    (numbers.PositiveInt, "10", 10),
    (numbers.PositiveInt, "-10", None),
    (numbers.NegativeInt, "-10", -10),
    (numbers.NegativeInt, "10", None),
]


@pytest.mark.parametrize(("cls", "value", "result"), INTS)
def test_custom_int_types(cls, value, result: int):
    @arc.command
    def command(val: cls):
        return val

    if result is not None:
        assert arc.convert(value, cls) == result
        assert command(str(value)) == result

    else:
        with pytest.raises((errors.ConversionError, errors.ValidationError)):
            arc.convert(value, cls)

        # Don't bother testing integer values
        with pytest.raises(errors.InvalidParamValueError):
            assert command(str(value))


FLOATS = [
    (numbers.PositiveFloat, "1", 1.0),
    (numbers.PositiveFloat, "1.2", 1.2),
    (numbers.PositiveFloat, "12.3456", 12.3456),
    (numbers.PositiveFloat, "-1", None),
    (numbers.PositiveFloat, "-1.2", None),
    (numbers.PositiveFloat, "-12.3456", None),
    (numbers.NegativeFloat, "1", None),
    (numbers.NegativeFloat, "1.2", None),
    (numbers.NegativeFloat, "12.3456", None),
    (numbers.NegativeFloat, "-1", -1),
    (numbers.NegativeFloat, "-1.2", -1.2),
    (numbers.NegativeFloat, "-12.3456", -12.3456),
]


@pytest.mark.parametrize(("cls", "value", "result"), FLOATS)
def test_strict_floats(cls, value, result):
    @arc.command
    def command(val: cls):  # type: ignore
        return val

    if result is not None:
        assert command(value) == arc.convert(value, cls) == result

    else:
        with pytest.raises(errors.ValidationError):
            arc.convert(value, cls)

        with pytest.raises(errors.InvalidParamValueError):
            assert command(f"{value}") == cls(value) == float(value)
