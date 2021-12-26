from __future__ import annotations
import typing as t
from arc.types.params import special


if t.TYPE_CHECKING:
    from arc.context import Context


@special(default={})
class State(dict):
    """State object, extends `dict`"""

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as e:
            raise AttributeError(str(e)) from e

    def __setattr__(self, name: str, value):
        self[name] = value

    def __or__(self, other: t.Mapping[t.Any, t.Any]):
        return type(self)(super().__or__(other))

    @classmethod
    def __convert__(cls, _value, _info, ctx: Context):
        # To account for State subclassing we create a new
        # State object with cls(), then set that, as the
        # context's state object
        state = cls(ctx.state)
        ctx.state = state
        return state
