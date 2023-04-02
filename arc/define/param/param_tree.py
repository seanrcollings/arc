from __future__ import annotations

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from arc.define.param import Param

T = t.TypeVar("T", bound=type)


@dataclass
class ParamValue:
    value: t.Any
    param: Param[t.Any]


@dataclass
class ParamTree(t.Generic[T]):
    """Tree data stucture that represents all
    the param values for a particular command execution"""

    data: dict[str, ParamTree[t.Any] | ParamValue]
    cls: T

    def __getitem__(self, path: t.Sequence[str]) -> t.Any:
        curr = self.__get_from_path(path)
        return curr.value

    def __setitem__(self, path: t.Sequence[str], value: t.Any) -> None:
        curr = self.__get_from_path(path)
        curr.value = value

    def __get_from_path(self, path: t.Sequence[str]) -> ParamValue:
        if isinstance(path, str):
            path = (path,)

        curr: ParamTree[t.Any] | ParamValue = self

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

    def compile(self, include_hidden: bool = False) -> T:
        compiled: dict[str, t.Any] = {}
        for key, value in self.data.items():
            if isinstance(value, ParamTree):
                compiled[key] = value.compile(include_hidden)
            else:
                if value.param.expose or include_hidden:
                    compiled[key] = value.value

        return self.cls(**compiled)
