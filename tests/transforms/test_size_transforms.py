import pytest
from arc.transforms import size


def test_truncate():
    trunc = size.Truncate(5)

    assert trunc("123456789") == "12345"
    assert trunc("123") == "123"
    assert trunc([1, 2, 3, 4, 5, 6, 7, 8, 9]) == [1, 2, 3, 4, 5]


def test_pad():
    pad = size.Pad(5, "b")

    assert pad("a") == "abbbb"
    assert pad("aaaa") == "aaaab"
    assert pad("aaaaa") == "aaaaa"
    assert pad("aaaaaa") == "aaaaaa"
    assert pad("aaaaaaaaaa") == "aaaaaaaaaa"

    pad = size.Pad(5, [2])
    assert pad([1]) == [1, 2, 2, 2, 2]
    assert pad([1, 1, 1, 1]) == [1, 1, 1, 1, 2]
    assert pad([1, 1, 1, 1, 1]) == [1, 1, 1, 1, 1]
    assert pad([1, 1, 1, 1, 1, 1, 1]) == [1, 1, 1, 1, 1, 1, 1]
