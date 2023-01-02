from __future__ import annotations
import typing as t
from dataclasses import dataclass


if t.TYPE_CHECKING:
    from arc.core.param import Param


@dataclass
class ParamValue:
    value: t.Any
    param: Param


@dataclass
class ParamTree:
    """Tree data stucture that represents all
    the param values for a particular command execution"""

    data: dict[str, ParamTree | ParamValue]
    cls: type

    def __getitem__(self, path: t.Sequence[str]):
        curr = self.__get_from_path(path)
        return curr.value

    def __setitem__(self, path: t.Sequence[str], value: t.Any):
        curr = self.__get_from_path(path)
        curr.value = value

    def __get_from_path(self, path: t.Sequence[str]) -> ParamValue:
        if isinstance(path, str):
            path = (path,)

        curr: ParamTree | ParamValue = self

        for component in path:
            if isinstance(curr, ParamTree):
                curr = curr.data[component]
            else:
                raise KeyError(f"{path} not a valid keypath")

        if not isinstance(curr, ParamValue):
            raise KeyError(f"{path} not a valid keypath")

        return curr

    def values(self) -> t.Generator[ParamValue, None, None]:
        for value in self.data.values():
            if isinstance(value, ParamTree):
                yield from value.values()
            else:
                yield value

    def compile(self, include_hidden: bool = False):
        compiled: dict[str, t.Any] = {}
        for key, value in self.data.items():
            if isinstance(value, ParamTree):
                compiled[key] = value.compile(include_hidden)
            else:
                if value.param.expose or include_hidden:
                    compiled[key] = value.value

        return self.cls(**compiled)
