from __future__ import annotations

import typing as t

from arc import errors
from arc.types.default import isdefault, unwrap

T = t.TypeVar("T")


class TypeArg:
    __slots__: tuple[str, ...]

    def __repr__(self) -> str:
        values = ", ".join(
            [f"{member}={repr(getattr(self, member))}" for member in self.__slots__]
        )
        return f"{type(self).__name__}({values})"

    def __setattr__(self, __name: str, __value: t.Any) -> None:
        raise TypeError(f"{type(self)} is readonly")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeArg):
            return NotImplemented
        return all(
            getattr(self, attr) == getattr(other, attr) for attr in self.__slots__
        )

    def __iter__(self) -> t.Iterator[t.Tuple[str, t.Any]]:
        for slot in self.__slots__:
            yield slot, getattr(self, slot)

    def __or__(self, other: TypeArg) -> TypeArg:
        merged: dict[str, t.Any] = {}

        for (attr, value), (_, other_value) in zip(self, other):
            if isdefault(other_value):
                merged[attr] = value
            else:
                merged[attr] = other_value

        return type(self)(**merged)

    def __hash__(self) -> int:
        return id(self)

    def __init_subclass__(cls) -> None:
        init: t.Callable[..., None] = getattr(cls, "__init__")
        setattr: t.Callable[..., None] = cls.__setattr__

        def __init__(self: object, *args: t.Any, **kwargs: t.Any) -> None:
            cls.__setattr__ = object.__setattr__  # type: ignore
            init(self, *args, **kwargs)
            cls.__setattr__ = setattr  # type: ignore

        cls.__init__ = __init__  # type: ignore

    def dict(self, unwrap_defaults: bool = True) -> dict[str, t.Any]:

        return {
            attr: unwrap(getattr(self, attr))
            if unwrap_defaults
            else getattr(self, attr)
            for attr in self.__slots__
        }

    @staticmethod
    def ensure(arg: T | None, name: str) -> T:
        if not arg:
            raise errors.TypeArgError(f"{name} requires a type argument")

        return arg
