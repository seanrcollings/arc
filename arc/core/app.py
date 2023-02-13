from __future__ import annotations
import typing as t

import arc
from arc import errors
from arc import typing as at
from arc import utils
from arc.config import Config
from arc.color import fg, colorize
from arc.logging import logger

from arc.core.middleware import *

if t.TYPE_CHECKING:
    from arc.core import Command


class App:
    DEFAULT_INIT_MIDDLEWARES = [
        AddUsageErrorInfoMiddleware,
        InitChecksMiddleware,
        InputMiddleware,
        CommandFinderMiddleware,
        ArgParseMiddleware,
        ParseResultCheckerMiddleware,
    ]

    DEFAULT_EXEC_MIDDLEWARES = [
        ExitStackMiddleware,
        SetupParamMiddleware,
        ApplyParseResultMiddleware,
        GetEnvValueMiddleware,
        GetPromptValueMiddleware,
        GetterValueMiddleware,
        ConvertValuesMiddleware,
        DefaultValueMiddleware,
        DependancyInjectorMiddleware,
        RunTypeMiddlewareMiddleware,
        OpenResourceMiddleware,
        MissingParamsCheckerMiddleware,
        CompileParamsMiddleware,
        DecoratorStackMiddleware,
        ExecutionHandler,
    ]

    def __init__(
        self,
        root: Command,
        config: Config,
        init_middlewares: list[type[Middleware]] | None = None,
        exec_middlewares: list[type[Middleware]] | None = None,
        input: at.InputArgs = None,
        state: dict[str, t.Any] = None,
        env: at.ExecEnv | None = None,
    ) -> None:
        self.root: Command = root
        self.config: Config = config
        self.init_middleware_types: list[type[Middleware]] = (
            init_middlewares or self.DEFAULT_INIT_MIDDLEWARES
        )
        self.exec_middleware_types: list[type[Middleware]] = (
            exec_middlewares or self.DEFAULT_EXEC_MIDDLEWARES
        )
        self.provided_env: at.ExecEnv = env or {}
        self.input: at.InputArgs = input
        self.state = state or {}

    __repr__ = utils.display("root")

    def __call__(self) -> t.Any:
        if not self.root.explicit_name:
            name = sys.argv[0]
            self.root.name = os.path.basename(name)

        first = self.build_middleware_stack(
            self.init_middleware_types + self.exec_middleware_types
        )
        try:
            return first(self.create_ctx())

        except errors.ExternalError as e:
            if self.config.environment == "production":
                arc.err(e)
                raise errors.Exit(1)

            raise
        except Exception as e:
            if self.config.report_bug:
                raise errors.InternalError(
                    f"{self.root.name} has encountered a critical error. "
                    f"Please file a bug report with the maintainer: {colorize(self.config.report_bug, fg.YELLOW)}"
                ) from e

            raise

    def execute(self, command: Command, **kwargs) -> t.Any:
        tree = command.param_def.create_instance()

        for key, value in kwargs.items():
            tree[key] = value

        ctx = self.create_ctx(
            {"arc.command": command, "arc.args.tree": tree, "arc.parse.result": {}}
        )
        first = self.build_middleware_stack(self.exec_middleware_types)
        return first(ctx)

    def build_middleware_stack(
        self, middlewares: t.Sequence[type[Middleware]]
    ) -> Middleware:
        first: Middleware | None = None

        for middleware_type in reversed(middlewares):
            if first is None:
                first = middleware_type(lambda env: env)
            else:
                first = middleware_type(first)

        assert first is not None

        return first

    def create_ctx(self, data: dict = None) -> Context:
        return Context(
            {
                "arc.root": self.root,
                "arc.input": self.input,
                "arc.config": self.config,
                "arc.errors": [],
                "arc.app": self,
                "arc.logger": logger,
                "arc.state": self.state,
            }
            | self.provided_env
            | (data or {})
        )

    @classmethod
    def __depends__(cls, ctx: Context):
        return ctx.app
