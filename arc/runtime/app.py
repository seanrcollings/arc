from __future__ import annotations
import os
import sys
import typing as t

import arc
import arc.typing as at
from arc import errors
from arc.config import config
from arc.logging import logger
from arc.runtime.init import DEFAULT_INIT_MIDDLEWARES
from arc.runtime.middleware import Middleware, MiddlewareContainer

if t.TYPE_CHECKING:
    from arc.define import Command
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

    def __call__(self, input: at.InputArgs = None) -> t.Any:
        self.handle_dynamic_name()
        ctx = self.create_ctx({"arc.input": input})
        try:
            try:
                ctx = self.stack.start(ctx)
                if "arc.command" not in ctx:
                    raise errors.CommandError(
                        "The command was not decided upon during initialization "
                        "(ctx['arc.command'] is not set). This likely means there "
                        "is a problem with your middleware stack"
                    )

                command: Command = ctx["arc.command"]
                res = None
                res = command.run(ctx)
            except Exception as e:
                res = None
                self.stack.throw(e)
            else:
                res = self.stack.close(res)
        except errors.ExternalError as exc:
            if self.config.environment == "production":
                arc.err(exc)
                arc.exit(1)

            raise
        except errors.Exit as exc:
            if exc.message:
                arc.err(exc.message)
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
                "arc.logger": logger,
            }
            | self.provided_ctx
            | (data or {})
        )

    def handle_dynamic_name(self):
        if not self.root.explicit_name:
            name = sys.argv[0]
            self.root.name = os.path.basename(name)
