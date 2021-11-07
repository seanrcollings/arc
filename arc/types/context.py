"""
.. include:: ../../wiki/Context.md
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from arc.types.params import as_special_param

if TYPE_CHECKING:
    from arc.execution_state import ExecutionState


@as_special_param()
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
