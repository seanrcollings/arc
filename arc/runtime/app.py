from __future__ import annotations

import os
import sys
import typing as t

import arc
import arc.typing as at
from arc import errors
from arc.logging import WARNING, logger, mode_map, DEBUG
from arc.runtime.init import InitMiddleware
from arc.runtime.middleware import Middleware, MiddlewareContainer


if t.TYPE_CHECKING:
    from arc.define import Command


class App(MiddlewareContainer):
    def __init__(
        self,
        root: Command,
        init_middlewares: t.Sequence[Middleware] = None,
        state: dict[str, t.Any] = None,
        ctx: dict[str, t.Any] = None,
    ) -> None:
        super().__init__(init_middlewares or InitMiddleware.all())
        self.root = root
        self.provided_ctx = ctx or {}
        self.state = state or {}
        self.config = root.config

    def __call__(self, input: at.InputArgs = None) -> t.Any:
        self._handle_dynamic_name()
        self._setup_logger()
        ctx = self._create_ctx({"arc.input": input})
        try:
            try:
                ctx = self.stack.start(ctx)
                if "arc.command" not in ctx:
                    raise errors.CommandError(
                        "The command was not decided upon during initialization "
                        "(ctx['arc.command'] is not set). This likely means there "
                        "is a problem with the middleware stack"
                    )

                command: Command = ctx["arc.command"]
                res = None
                res = command.run(ctx)
            except Exception as e:
                res = None
                self.stack.throw(e)
            else:
                res = self.stack.close(res)
        except errors.ArcError as exc:
            if self.config.environment == "production":
                arc.info(exc.fmt(ctx))
                arc.exit(1)

            raise
        except errors.Exit as exc:
            if exc.message:
                arc.info(exc.fmt(ctx))
            raise

        return res

    def execute(self, command: Command, **kwargs: t.Any) -> t.Any:
        ctx = self._create_ctx({"arc.command": command, "arc.parse.result": kwargs})
        return command.run(ctx)

    def _create_ctx(self, data: dict[str, t.Any] = None) -> arc.Context:
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

    def _handle_dynamic_name(self) -> None:
        if not self.root.explicit_name:
            name = sys.argv[0]
            self.root.name = os.path.basename(name)

    def _setup_logger(self) -> None:
        if self.config.debug:
            logger.setLevel(DEBUG)
        else:
            logger.setLevel(mode_map.get(self.config.environment, WARNING))
