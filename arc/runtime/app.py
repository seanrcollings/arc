from __future__ import annotations
import logging
import os
import sys
import typing as t

import arc
from arc.runtime.daemon import Daemon
import arc.typing as at
from arc import errors
from arc.logging import logger, mode_map
from arc.runtime.init import InitMiddleware
from arc.runtime.middleware import Middleware, MiddlewareManager
from arc.runtime.plugin import PluginManager
from arc.runtime.serve import Server

if t.TYPE_CHECKING:
    from arc.define import Command


class App(MiddlewareManager):
    def __init__(
        self,
        root: Command,
        init_middlewares: t.Sequence[Middleware] = None,
        state: dict[str, t.Any] = None,
        ctx: dict[str, t.Any] = None,
        logger: logging.Logger = logger,
    ) -> None:
        super().__init__(init_middlewares or InitMiddleware.all())
        self.root = root
        self.provided_ctx = ctx or {}
        self.state = state or {}
        self.config = root.config
        self.plugins = PluginManager()
        self.logger = logger

    def __call__(
        self, input: at.InputArgs = None, ctx: dict[str, t.Any] | None = None
    ) -> t.Any:
        self._handle_dynamic_name()
        self._setup_logger()
        ctx = ctx or {}
        context_obj = self._create_ctx({"arc.input": input, **ctx})
        try:
            try:
                context_obj = self._stack.start(context_obj)
                if "arc.command" not in context_obj:
                    raise errors.CommandError(
                        "The command was not decided upon during initialization "
                        "(ctx['arc.command'] is not set). This likely means there "
                        "is a problem with the middleware stack"
                    )

                command: Command = context_obj["arc.command"]
                res = None
                res = command.run(context_obj)
            except Exception as e:
                res = None
                self._stack.throw(e)
            else:
                res = self._stack.close(res)
        except errors.ArcError as exc:
            if self.config.environment == "production":
                arc.info(exc.fmt(context_obj))
                arc.exit(1)

            raise
        except errors.Exit as exc:
            if exc.message:
                arc.info(exc.fmt(context_obj))
            raise

        return res

    @classmethod
    def __depends__(self, ctx: arc.Context) -> App:
        return ctx.app

    def serve(self, address: at.Address) -> None:
        self._setup_logger()
        self.logger.info(f"Starting server on {address}")

        with Server(self, address) as server:
            server.serve()

        self.logger.info(f"Stopping server on {address}")

    def execute(self, command: Command, **kwargs: t.Any) -> t.Any:
        ctx = self._create_ctx({"arc.command": command, "arc.parse.result": kwargs})
        return command.run(ctx)

    def _create_ctx(self, data: dict[str, t.Any] = None) -> arc.Context:
        return arc.Context(
            {
                "arc.root": self.root,
                "arc.config": self.config,
                "arc.app": self,
                "arc.state": self.state,
                "arc.logger": self.logger,
                "arc.plugins": self.plugins,
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
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(mode_map.get(self.config.environment, logging.WARNING))
