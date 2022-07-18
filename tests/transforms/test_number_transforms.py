from arc.transforms import numbers


def test_round():
    assert numbers.Round(2)(1.23456) == 1.23
