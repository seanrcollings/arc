from _pytest.monkeypatch import V
import pytest
import arc
from arc.types import numbers
from arc import errors

INTS = [
    (numbers.Binary, "11", True),
    (numbers.Binary, "1111101010101", True),
    (numbers.Binary, 99, True),
    (numbers.Binary, "2", False),
    (numbers.Binary, "string", False),
    (numbers.Oct, "10", True),
    (numbers.Oct, 10, True),
    (numbers.Oct, "7", True),
    (numbers.Oct, "8", False),
    (numbers.Oct, "99", False),
    (numbers.Oct, "fff", False),
    (numbers.Hex, "1", True),
    (numbers.Hex, 1, True),
    (numbers.Hex, "fff", True),
    (numbers.PositiveInt, "10", True),
    (numbers.PositiveInt, "-10", False),
    (numbers.NegativeInt, "-10", True),
    (numbers.NegativeInt, "10", False),
]


@pytest.mark.parametrize(("cls", "value", "passes"), INTS)
def test_strict_ints(cls, value, passes):
    @arc.command()
    def command(val: cls):  # type: ignore
        return val

    if passes:
        converted = value
        if not isinstance(value, int):
            converted = int(value, base=cls.base)

        assert cls(value) == converted

        # Don't bother testing integer values
        if not isinstance(value, int):
            assert command(str(value)) == converted

    else:
        with pytest.raises(ValueError):
            cls(value)

        # Don't bother testing integer values
        if not isinstance(value, int):
            with pytest.raises(errors.InvalidArgValue):
                assert command(str(value))


FLOATS = [
    (numbers.PositiveFloat, "1", True),
    (numbers.PositiveFloat, "1.2", True),
    (numbers.PositiveFloat, "12.3456", True),
    (numbers.PositiveFloat, 12.3456, True),
    (numbers.PositiveFloat, "-1", False),
    (numbers.PositiveFloat, "-1.2", False),
    (numbers.PositiveFloat, "-12.3456", False),
    (numbers.PositiveFloat, -12.3456, False),
    (numbers.NegativeFloat, "1", False),
    (numbers.NegativeFloat, "1.2", False),
    (numbers.NegativeFloat, "12.3456", False),
    (numbers.NegativeFloat, 12.3456, False),
    (numbers.NegativeFloat, "-1", True),
    (numbers.NegativeFloat, "-1.2", True),
    (numbers.NegativeFloat, "-12.3456", True),
    (numbers.NegativeFloat, -12.3456, True),
]


@pytest.mark.parametrize(("cls", "value", "passes"), FLOATS)
def test_strict_floats(cls, value, passes):
    @arc.command()
    def command(val: cls):  # type: ignore
        return val

    if passes:
        assert cls(value) == float(value)

        if not isinstance(value, float):
            assert command(f"{value}") == cls(value) == float(value)

    else:
        with pytest.raises(ValueError):
            cls(value)

        if not isinstance(value, float):
            with pytest.raises(errors.InvalidArgValue):
                assert command(f"{value}") == cls(value) == float(value)


@pytest.mark.parametrize(("cls", "value", "passes"), INTS + FLOATS)  # type: ignore
def test_any_number(cls, value, passes):
    if not isinstance(value, str):
        return

    @arc.command()
    def command(val: cls):  # type: ignore
        return val

    if passes:
        assert command(f"{value}") == cls(value)
    else:
        with pytest.raises(errors.InvalidArgValue):
            command(f"{value}")


# def test_int_matches():
#     MatchInt = numbers.strictint(matches=r"^\d*1$")
#     assert MatchInt("1") == 1
#     assert MatchInt("555551") == 555551
#     assert MatchInt("10000000000000000001") == 10000000000000000001

#     with pytest.raises(ValueError):
#         MatchInt("5")


# def test_float_matches():
#     MatchFloat = numbers.strictfloat(matches=r"^\d*\.0+1$")
#     assert MatchFloat("1.01") == 1.01
#     assert MatchFloat("5555.000000001") == 5555.000000001

#     with pytest.raises(ValueError):
#         MatchFloat("231.1")


# def test_max_precision():
#     MaxPercision = numbers.strictfloat(max_precision=10)
#     assert MaxPercision("1.1123124111") == 1.1123124111

#     with pytest.raises(ValueError):
#         MaxPercision("1.112312411111111")


# def test_min_precision():
#     MinPrecision = numbers.strictfloat(min_precision=5)
#     assert MinPrecision("1.1123124111") == 1.1123124111
#     assert MinPrecision("1.11211") == 1.11211

#     with pytest.raises(ValueError):
#         MinPrecision("1.1")


# def test_precision():
#     Precision = numbers.strictfloat(precision=5)
#     assert Precision("1.12345") == 1.12345
#     assert Precision("1.11211") == 1.11211

#     with pytest.raises(ValueError):
#         Precision("1.1")
