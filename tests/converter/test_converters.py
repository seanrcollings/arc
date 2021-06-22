import pytest
from typing import Literal
from enum import Enum, IntEnum

from arc.convert import *
from arc.errors import ConversionError, ArcError
from arc.types import Range


def test_int():
    assert IntConverter().convert("1") == 1
    assert IntConverter().convert("2") == 2
    assert IntConverter().convert("213131") == 213131

    with pytest.raises(ConversionError):
        IntConverter().convert("no numbers")


def test_float():
    assert FloatConverter().convert("1") == 1.0
    assert FloatConverter().convert("1.2") == 1.2
    assert FloatConverter().convert("2.32") == 2.32
    assert FloatConverter().convert("213.131") == 213.131

    with pytest.raises(ConversionError):
        FloatConverter().convert("no numbers")


def test_byte():
    assert BytesConverter(bytes).convert("string") == b"string"


def test_list():
    assert ListConverter().convert("1,2,3") == ["1", "2", "3"]
    assert ListConverter().convert("a,b,c") == ["a", "b", "c"]
    assert ListConverter().convert("a") == ["a"]


def test_bool():
    assert BoolConverter().convert("0") == False
    assert BoolConverter().convert("1") == True

    assert BoolConverter().convert("True") == True
    assert BoolConverter().convert("T") == True
    assert BoolConverter().convert("true") == True
    assert BoolConverter().convert("t") == True

    assert BoolConverter().convert("False") == False
    assert BoolConverter().convert("F") == False
    assert BoolConverter().convert("false") == False
    assert BoolConverter().convert("f") == False

    with pytest.raises(ConversionError):
        BoolConverter().convert("ainfeainfeain")


def test_enum():
    class Color(Enum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    assert EnumConverter(Color).convert("red") == Color.RED
    assert EnumConverter(Color).convert("green") == Color.GREEN
    assert EnumConverter(Color).convert("blue") == Color.BLUE

    with pytest.raises(ConversionError):
        EnumConverter(Color).convert("yellow")

    with pytest.raises(ConversionError):
        EnumConverter(Color).convert("2")


def test_numbered_enum():
    class Numbers(Enum):
        ONE = 1
        TWO = 2
        THREE = 3

    assert EnumConverter(Numbers).convert("1") == Numbers.ONE
    assert EnumConverter(Numbers).convert("2") == Numbers.TWO
    assert EnumConverter(Numbers).convert("3") == Numbers.THREE

    with pytest.raises(ConversionError):
        EnumConverter(Numbers).convert("4")


def test_int_enum():
    class Numbers(IntEnum):
        ONE = 1
        TWO = 2
        THREE = 3

    assert EnumConverter(Numbers).convert("1") == Numbers.ONE
    assert EnumConverter(Numbers).convert("2") == Numbers.TWO
    assert EnumConverter(Numbers).convert("3") == Numbers.THREE

    with pytest.raises(ConversionError):
        EnumConverter(Numbers).convert("4")


def test_range():
    assert RangeConverter(Range[Literal[1], Literal[10]]).convert("2") == 2
    assert RangeConverter(Range[Literal[1], Literal[10]]).convert("1") == 1
    assert RangeConverter(Range[Literal[1], Literal[10]]).convert("8") == 8

    with pytest.raises(ConversionError):
        RangeConverter(Range[Literal[1], Literal[10]]).convert("10")

    with pytest.raises(ConversionError):
        RangeConverter(Range[Literal[5], Literal[10]]).convert("3")

    with pytest.raises(ArcError):
        RangeConverter(Range[Literal[5], Literal["string"]]).convert("3")
