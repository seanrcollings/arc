from __future__ import annotations
import typing as t
import collections

from arc.constants import MISSING
from arc import errors
from .param import Param


class ParamDefinition(collections.UserList[Param]):
    BASE = "__arc_param_group_base"
    """A group with name `BASE` is the base group and
    gets spread into the function arguments"""
    children: list[ParamDefinition]

    def __init__(self, name: str, cls: type | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.cls = cls
        self.children = []

    def __repr__(self):
        return f"ParamGroup(name={self.name!r}, params={self.data!r})"

    def all_params(self) -> t.Generator[Param, None, None]:
        """Generator that yields all params in itself, and in it's sub groups recursivley"""
        yield from self.data

        if self.children:
            for child in self.children:
                yield from child.all_params()

    @property
    def is_base(self) -> bool:
        return self.name == self.BASE

    @classmethod
    def get_base_group(cls, groups: list[ParamDefinition]) -> ParamDefinition:
        for group in groups:
            if group.is_base:
                return group

        raise errors.InternalError("No base param group found")


class ParamValueNode:
    values: dict[str, t.Any]
    cls: type
    children: list[ParamValueNode]

    def __init__(self):
        ...
