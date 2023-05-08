from __future__ import annotations

import typing as t

from arc import logging
from arc.define.param import ValueOrigin

if t.TYPE_CHECKING:
    from arc import Context
    from arc.define.param import Param


class Log:
    """Type middleware to log the value provided

    ## Example
    ```py
    import typing as t
    import arc
    from arc.types.middleware import Log

    arc.configure(environment="development")


    @arc.command
    def command(
        val: t.Annotated[int, Log()],
        flag_name: t.Annotated[bool, Log()],
    ):
        arc.print("hello there!")


    command()
    ```
    """

    def __init__(
        self,
        level: int = logging.INFO,
        name_kind: t.Literal["arg", "param", "cli"] = "arg",
    ) -> None:
        self.level = level
        self.name_kind = name_kind

    def __call__(
        self,
        value: t.Any,
        ctx: Context | None = None,
        param: Param[t.Any] | None = None,
    ) -> t.Any:
        if param and ctx:
            names = {
                "arg": param.argument_name,
                "param": param.param_name,
                "cli": param.cli_name,
            }

            origin = ctx.get_origin(param.argument_name, ValueOrigin.DEFAULT)
            name = names.get(self.name_kind, param.argument_name)

            ctx.logger.log(self.level, f"{name} = {value} ({origin.value})")

        return value
