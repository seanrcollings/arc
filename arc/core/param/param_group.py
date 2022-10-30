from __future__ import annotations
import typing as t
import collections

from arc.constants import MISSING
from arc import errors
import arc.typing as at
from .param import InjectedParam, Param

if t.TYPE_CHECKING:
    from arc.context import Context


class ParamGroup(collections.UserList[Param]):
    DEFAULT = "default"
    """A group with name `DEFAULT` is the base group and
    gets spread into the function arguments"""
    sub_groups: list[ParamGroup]

    def __init__(self, name: str, cls: type | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.cls = cls
        self.sub_groups = []

    def __repr__(self):
        return f"ParamGroup(name={self.name!r}, params={self.data!r})"

    def all_params(self) -> t.Generator[Param, None, None]:
        """Generator that yields all params in itself, and in it's sub groups recursivley"""
        yield from self.data

        if self.sub_groups:
            for sub in self.sub_groups:
                yield from sub.all_params()

    @property
    def is_default(self) -> bool:
        return self.name == self.DEFAULT

    @classmethod
    def get_default_group(cls, groups: list[ParamGroup]) -> ParamGroup:
        for group in groups:
            if group.is_default:
                return group

        raise errors.InternalError("No default param group found")
