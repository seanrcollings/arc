"""
.. include:: ../../wiki/Context.md
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Annotated
from arc.types.helpers import is_annotated
from arc.command.param import ParamType
from arc.types import Meta

if TYPE_CHECKING:
    from arc.execution_state import ExecutionState


# Because Context is subclassable, we
# need to make sure to wrap it's child classes
# in the Annotated wrapper for the Context to function
# properly
class ContextMeta(type):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        if not is_annotated(obj):
            annotated = Annotated[
                obj, Meta(hidden=True, type=ParamType.SPECIAL, hooks=[obj.from_state])
            ]
            return annotated
        return obj


class Context(dict, metaclass=ContextMeta):
    """Context object, extends `dict`"""

    state: ExecutionState

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f" : {' '.join(key + '=' + str(value) for key, value in self.items())}>"
        )

    def __getattr__(self, attr):
        return self[attr]

    @classmethod
    def from_state(cls, _value, state: ExecutionState):
        ctx: dict = {}
        for command in state.command_chain:
            ctx = command.context | ctx
            ctx["state"] = state

        return cls(ctx)
