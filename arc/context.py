from __future__ import annotations
import typing as t

import arc.typing as at

if t.TYPE_CHECKING:
    from arc.core.param.param import ValueOrigin
    from arc.core.command import Command
    from arc.core.app import Arc
    from logging import Logger
    from arc.config import Config


T = t.TypeVar("T")


class Context:
    """Context serves as a "view" into the execution enviroment"""

    def __init__(self, env: at.ExecEnv) -> None:
        self.env: at.ExecEnv = env

    @property
    def command(self) -> Command:
        return self.env["arc.command"]

    @property
    def state(self) -> dict:
        return self.env["arc.state"]

    @property
    def logger(self) -> Logger:
        return self.env["arc.logger"]

    @property
    def app(self) -> Arc:
        return self.env["arc.app"]

    @property
    def config(self) -> Config:
        return self.env["arc.config"]

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
        origins: dict[str, ValueOrigin] | None = self.env.get("arc.args.origins")

        if not origins:
            return default

        return origins.get(param_name, default)

    @classmethod
    def __depends__(cls, ctx: Context):
        return ctx
