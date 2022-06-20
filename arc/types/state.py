from __future__ import annotations
import collections
import typing as t


if t.TYPE_CHECKING:
    from arc.context import Context


class State(collections.UserDict):
    """State object"""

    def __repr__(self):
        values = ", ".join(f"{key}={value}" for key, value in self.data.items())
        return f"{self.__class__.__name__}({values})"

    def __getattr__(self, attr):
        try:
            return self.data[attr]
        except KeyError as e:
            raise AttributeError(str(e)) from e

    def __setattr__(self, name: str, value):
        if name == "data":
            super().__setattr__(name, value)
        else:
            self.data[name] = value

    @classmethod
    def __depends__(cls, ctx: Context):
        state = cls()
        state.data = ctx.state.data
        return state
