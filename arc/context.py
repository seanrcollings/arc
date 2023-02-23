from __future__ import annotations
import collections
import typing as t

import arc.typing as at

if t.TYPE_CHECKING:
    from arc.define.param.param import ValueOrigin
    from arc.define.command import Command
    from arc.runtime import App
    from logging import Logger
    from arc.config import Config


T = t.TypeVar("T")


class Context(collections.UserDict[str, t.Any]):
    """Context serves as a "view" into the execution enviroment"""

    @property
    def command(self) -> Command:
        return self["arc.command"]

    @property
    def state(self) -> dict:
        return self["arc.state"]

    @property
    def logger(self) -> Logger:
        return self["arc.logger"]

    @property
    def app(self) -> App:
        return self["arc.app"]

    @property
    def config(self) -> Config:
        return self["arc.config"]

    def execute(self, command: Command, **kwargs) -> t.Any:
        """Execute a command within the context of another command"""
        return self.app.execute(command, **kwargs)

    @t.overload
    def get_origin(self, param_name: str) -> ValueOrigin | None:
        ...

    @t.overload
    def get_origin(self, param_name: str, default: T) -> ValueOrigin | T:
        ...

    def get_origin(self, param_name: str, default=None):
        """Gets the origin of a paramter"""
        origins: dict[str, ValueOrigin] | None = self.get("arc.args.origins")

        if not origins:
            return default

        return origins.get(param_name, default)

    @classmethod
    def __depends__(cls, ctx: Context):
        return ctx
