from __future__ import annotations
from arc.types.default import isdefault, unwrap


class TypeArg:
    __slots__: tuple[str, ...]

    # def __setattr__(self, __name: str, __value: t.Any) -> None:
    #     raise RuntimeError("TypeArgs cannot be modified")

    def __eq__(self, other: object):
        if not isinstance(other, TypeArg):
            return NotImplemented
        return all(
            getattr(self, attr) == getattr(other, attr) for attr in self.__slots__
        )

    def __iter__(self):
        for slot in self.__slots__:
            yield slot, getattr(self, slot)

    def __or__(self, other: TypeArg):
        merged: dict = {}

        for (attr, value), (_, other_value) in zip(self, other):
            if isdefault(other_value):
                merged[attr] = value
            else:
                merged[attr] = other_value

        return type(self)(**merged)  # type: ignore

    def __hash__(self):
        return id(self)

    def dict(self, unwrap_defaults: bool = True):
        return {
            attr: unwrap(getattr(self, attr))
            if unwrap_defaults
            else getattr(self, attr)
            for attr in self.__slots__
        }
