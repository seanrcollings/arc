"""
.. include:: ../../wiki/Context.md
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arc.execution_state import ExecutionState


class Context(dict):
    """Context object, extends `dict`"""

    execution_state: "ExecutionState"

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f" : {' '.join(key + '=' + str(value) for key, value in self.items())}>"
        )

    def __getattr__(self, attr):
        return self[attr]
