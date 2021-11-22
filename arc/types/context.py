"""
.. include:: ../../wiki/Context.md
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any
from arc.types.params import as_special_param
from arc.utils import symbol

MISSING = symbol("MISSING")

if TYPE_CHECKING:
    from arc.execution_state import ExecutionState


@as_special_param(default={})
class Context(dict):
    """Context object, extends `dict`"""

    state: ExecutionState

    def __repr__(self):
        values = [f"{key}={value}" for key, value in self.items() if key != "state"]
        return f"<{self.__class__.__name__} : {' '.join(values)}>"

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, name: str, value):
        return self.__setitem__(name, value)

    class Config:
        name = "Context"
        allow_missing = True

    @classmethod
    def __convert__(cls, value: Any, _, state: ExecutionState):
        ctx: dict[str, Any] = {}

        ctx |= value

        for command in state.command_chain:
            ctx = command.context | ctx

        ctx["state"] = state

        return cls(ctx)

    def __cleanup__(self, _):
        """Empty Cleanup Function Because
        __getattr__ raises a KeyError otherwise
        when checking for a cleanup function"""
