import typing as t
from arc.context import Context
import arc.typing as at


class Middleware:
    def __init__(self) -> None:
        self.app = lambda ctx: None

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.app!r})"

    def __call__(self, ctx: Context) -> t.Any:
        return self.app(ctx)
