from __future__ import annotations

import collections
import typing as t

if t.TYPE_CHECKING:
    from arc.runtime import Context


class State(collections.UserDict[str, t.Any]):
    """State object"""

    def __repr__(self) -> str:
        values = ", ".join(f"{key}={value!r}" for key, value in self.data.items())
        return f"{self.__class__.__name__}({values})"

    def __getattr__(self, attr: str) -> t.Any:
        try:
            return self.data[attr]
        except KeyError as e:
            raise AttributeError(str(e)) from e

    def __setattr__(self, name: str, value: t.Any) -> None:
        if name == "data":
            super().__setattr__(name, value)
        else:
            self.data[name] = value

    @classmethod
    def __depends__(cls, ctx: Context) -> State:
        state = cls()
        state.data = ctx["arc.state"]
        return state
