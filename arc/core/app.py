from __future__ import annotations
import typing as t

import arc
from arc import errors
from arc.config import config
from arc.core.middleware.init import DEFAULT_INIT_MIDDLEWARES
from arc.core.middleware.middleware import Middleware, MiddlewareContainer
import arc.typing as at

if t.TYPE_CHECKING:
    from arc.core import Command
    from arc.config import Config


class App(MiddlewareContainer):
    def __init__(
        self,
        root: Command,
        config: Config = config,
        init_middlewares: t.Sequence[Middleware] = None,
        state: dict[str, t.Any] = None,
        ctx: dict[str, t.Any] = None,
    ) -> None:
        super().__init__(init_middlewares or DEFAULT_INIT_MIDDLEWARES)
        self.root = root
        self.config = config
        self.provided_ctx = ctx or {}
        self.state = state or {}

    def __call__(self, input=None) -> t.Any:
        ctx = self.create_ctx({"arc.input": input})
        ctx = self.stack.start(ctx)
        command: Command = ctx["arc.command"]
        res = None

        try:
            try:
                res = command.run(ctx)
            except Exception as e:
                res = None
                self.stack.throw(e)
            else:
                res = self.stack.close(res)
        except errors.ExternalError as exc:
            if self.config.environment == "production":
                print(exc)
                arc.exit(1)

            raise

        return res

    def execute(self, command: Command, **kwargs: t.Any) -> t.Any:
        ctx = self.create_ctx({"arc.command": command, "arc.parse.result": kwargs})
        return command.run(ctx)

    def create_ctx(self, data: dict = None) -> arc.Context:
        return arc.Context(
            {
                "arc.root": self.root,
                "arc.config": self.config,
                "arc.errors": [],
                "arc.app": self,
                "arc.state": self.state,
            }
            | self.provided_ctx
            | (data or {})
        )
