from __future__ import annotations
import typing as t

from arc.types.params import special
from arc.types.aliases import Alias
from arc.types.helpers import TypeInfo
from arc import utils

if t.TYPE_CHECKING:
    from arc.execution_state import ExecutionState

T = t.TypeVar("T")


@special(default=[])
class VarPositional(list[T]):
    @classmethod
    def __convert__(cls, _value, info: TypeInfo, state: ExecutionState):
        values = state.parsed["pos_values"]
        state.parsed["pos_values"] = []

        if info.sub_types:
            sub = info.sub_types[0]
            sub_cls = Alias.resolve(sub)
            values = [
                utils.dispatch_args(sub_cls.__convert__, value, sub, state)
                for value in values
            ]

        return values


@special(default={})
class VarKeyword(dict[str, T]):
    @classmethod
    def __convert__(cls, _value, info: TypeInfo, state: ExecutionState):
        assert state.executable
        kwargs = {
            name: value
            for name, value in state.parsed["key_values"].items()
            if name not in state.executable.key_params + state.executable.flag_params
        }
        state.parsed["key_values"] = {
            name: value
            for name, value in state.parsed["key_values"].items()
            if name not in kwargs
        }

        if info.sub_types:
            sub = info.sub_types[0]
            sub_cls = Alias.resolve(sub)
            kwargs = {
                name: utils.dispatch_args(sub_cls.__convert__, value, sub, state)
                for name, value in kwargs.items()
            }

        return kwargs
