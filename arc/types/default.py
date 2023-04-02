import typing as t


class DefaultValue:
    __slots__ = ("value",)

    def __init__(self, value: t.Any) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"Default({self.value!r})"

    def __repr__(self) -> str:
        return str(self)


def Default(value: t.Any) -> t.Any:
    return DefaultValue(value)


def unwrap(value: t.Any) -> t.Any:
    if isinstance(value, DefaultValue):
        return value.value

    return value


def isdefault(value: t.Any) -> bool:
    return isinstance(value, DefaultValue)
