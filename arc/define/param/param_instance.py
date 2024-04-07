from __future__ import annotations

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from arc.define.param import Param

T = t.TypeVar("T", bound=type)


@dataclass
class ParamInstanceLeafNode:
    name: str
    value: t.Any
    param: Param[t.Any]


@dataclass
class ParamInstanceInteriorNode(t.Generic[T]):
    """Tree data stucture that represents all
    the param values for a particular command execution"""

    name: str
    cls: T
    children: list[ParamInstanceInteriorNode[t.Any] | ParamInstanceLeafNode]

    def leaves(self) -> t.Generator[ParamInstanceLeafNode, None, None]:
        for value in self.children:
            if isinstance(value, ParamInstanceInteriorNode):
                yield from value.leaves()
            else:
                yield value

    def compile(self, include_hidden: bool = False) -> T:
        compiled = {}

        for child in self.children:
            if isinstance(child, ParamInstanceInteriorNode):
                compiled[child.name] = child.compile(include_hidden)
            else:
                if child.param.expose or include_hidden:
                    compiled[child.name] = child.value

        return self.cls(**compiled)


@dataclass
class ParamInstanceTree(t.Generic[T]):
    root: ParamInstanceInteriorNode[T]

    def __getitem__(self, path: t.Sequence[str]) -> t.Any:
        curr = self.__get_from_path(path)
        return curr.value

    def __setitem__(self, path: t.Sequence[str], value: t.Any) -> None:
        curr = self.__get_from_path(path)
        curr.value = value

    def __get_from_path(self, path: t.Sequence[str]) -> ParamInstanceLeafNode:
        if isinstance(path, str):
            path = (path,)

        curr: ParamInstanceInteriorNode[t.Any] | ParamInstanceLeafNode = self.root

        for component in path:
            if isinstance(curr, ParamInstanceInteriorNode):
                possbile_child = [
                    child for child in curr.children if child.name == component
                ]
                if not possbile_child:
                    raise KeyError(f"{path} not a valid keypath")

                curr = possbile_child[0]
            else:
                raise KeyError(f"{path} not a valid keypath")

        if not isinstance(curr, ParamInstanceLeafNode):
            raise KeyError(f"{path} not a valid keypath")

        return curr

    def leaves(self) -> t.Generator[ParamInstanceLeafNode, None, None]:
        return self.root.leaves()

    def compile(self, include_hidden: bool = False) -> T:
        return self.root.compile(include_hidden)
