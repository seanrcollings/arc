"""
.. include:: ../../wiki/Context.md
"""
from typing import TYPE_CHECKING, Annotated
from arc.types.helpers import is_annotated
from arc.command.param import ParamType
from arc.types import Meta

if TYPE_CHECKING:
    from arc.execution_state import ExecutionState


class ContextMeta(type):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        if not is_annotated(obj):
            annotated = Annotated[obj, Meta(hidden=True, type=ParamType.SPECIAL)]
            return annotated
        return obj


class Context(dict, metaclass=ContextMeta):
    """Context object, extends `dict`"""

    execution_state: "ExecutionState"

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f" : {' '.join(key + '=' + str(value) for key, value in self.items())}>"
        )

    def __getattr__(self, attr):
        return self[attr]
