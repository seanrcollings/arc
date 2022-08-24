import typing as t


class DefaultValue:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Default({self.value})"


def Default(value: t.Any) -> t.Any:
    return DefaultValue(value)


def unwrap(value):
    if isinstance(value, DefaultValue):
        return value.value

    return value


def isdefault(value):
    return isinstance(value, DefaultValue)
