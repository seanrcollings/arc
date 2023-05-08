from __future__ import annotations

import collections
import typing as t

import arc.typing as at

if t.TYPE_CHECKING:
    from logging import Logger

    from arc.config import Config
    from arc.define.command import Command
    from arc.define.param.param import ValueOrigin
    from arc.prompt.prompt import Prompt
    from arc.runtime import App


T = t.TypeVar("T")


class Context(collections.UserDict[str, t.Any]):
    """Context is a dict-like object that serves as
    the shared execution state for all `arc` component
    """

    @property
    def root(self) -> Command:
        """The root command object. Alias for `ctx["arc.root"]`"""
        return self["arc.root"]

    @property
    def command(self) -> Command:
        """The command object being executed. Alias for `ctx["arc.command"]`"""
        return self["arc.command"]

    @property
    def state(self) -> dict[str, t.Any]:
        """The state object passed in. Alias for `ctx["arc.state"]`"""
        return self["arc.state"]

    @property
    def logger(self) -> Logger:
        """The arc logger. Alias for `ctx["arc.logger"]`"""
        return self["arc.logger"]

    @property
    def app(self) -> App:
        """The arc app. Alias for `ctx["arc.app"]`"""
        return self["arc.app"]

    @property
    def config(self) -> Config:
        """The configuration for this app. Alias for `ctx["arc.config"]`"""
        return self["arc.config"]

    @property
    def prompt(self) -> Prompt:
        """The prompt object congigured. Alias for `ctx["arc.config"].prompt`"""
        return self.config.prompt

    def execute(self, command: Command, **kwargs: t.Any) -> t.Any:
        """Execute a command within the context of another command
        ```py
        import arc

        @arc.command
        def command(ctx: arc.Context):
            ctx.execute(sub, val=2)

        @command.subcommand
        def sub(val: int):
            print(sub)
        ```

        """
        return self.app.execute(command, **kwargs)

    @t.overload
    def get_origin(self, param_name: str) -> ValueOrigin | None:
        ...

    @t.overload
    def get_origin(self, param_name: str, default: T) -> ValueOrigin | T:
        ...

    def get_origin(
        self, param_name: str, default: T | None = None
    ) -> ValueOrigin | T | None:
        """Gets the origin of a paramter"""
        origins: dict[str, ValueOrigin] | None = self.get("arc.args.origins")

        if not origins:
            return default

        return origins.get(param_name, default)

    @classmethod
    def __depends__(cls, ctx: Context) -> Context:
        """Makes the context a dependency"""
        return ctx
