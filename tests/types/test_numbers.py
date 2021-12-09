from _pytest.monkeypatch import V
import pytest
from arc.types import numbers
from arc import CLI, errors

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
def test_strict_ints(cli: CLI, cls, value, passes):
    @cli.subcommand()
    def test(val: cls):  # type: ignore
        return val

    if passes:
        converted = value
        if not isinstance(value, int):
            converted = int(value, base=cls.base)

        assert cls(value) == converted

        # Don't bother testing integer values
        if not isinstance(value, int):
            assert cli(f"test {value}") == converted

    else:
        with pytest.raises(ValueError):
            cls(value)

        # Don't bother testing integer values
        if not isinstance(value, int):
            with pytest.raises(errors.InvalidParamaterError):
                assert cli(f"test {value}")


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
def test_strict_floats(cli: CLI, cls, value, passes):
    @cli.subcommand()
    def test(val: cls):  # type: ignore
        return val

    if passes:
        assert cls(value) == float(value)

        if not isinstance(value, float):
            assert cli(f"test {value}") == cls(value) == float(value)

    else:
        with pytest.raises(ValueError):
            cls(value)

        if not isinstance(value, float):
            with pytest.raises(errors.InvalidParamaterError):
                assert cli(f"test {value}") == cls(value) == float(value)


@pytest.mark.parametrize(("cls", "value", "passes"), INTS + FLOATS)  # type: ignore
def test_any_number(cli: CLI, cls, value, passes):
    if not isinstance(value, str):
        return

    @cli.subcommand()
    def test(val: cls):  # type: ignore
        return val

    if passes:
        assert cli(f"test {value}") == cls(value)
    else:
        with pytest.raises(errors.InvalidParamaterError):
            cli(f"test {value}")


class TestStrict:
    def test_matches(self):
        MatchInt = numbers.strictint(matches=r"^\d*1$")
        assert MatchInt("1") == 1
        assert MatchInt("555551") == 555551
        assert MatchInt("10000000000000000001") == 10000000000000000001

        with pytest.raises(ValueError):
            MatchInt("5")
