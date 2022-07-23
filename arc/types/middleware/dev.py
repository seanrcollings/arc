from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from arc._command.param import Param
    from arc import Context


class Log:
    """Type middleware to log the value provided

    ## Example
    ```py
    import typing as t
    import arc
    from arc.types.middleware import Log

    arc.configure(environment="development")


    @arc.command()
    def command(
        val: t.Annotated[int, Log()],
        flag_name: t.Annotated[bool, Log()],
        ctx: t.Annotated[arc.Context, Log()],
    ):
        print("hello there!")


    command()
    ```
    """

    def __init__(self, name_kind: t.Literal["arg", "param", "cli"] = "arg") -> None:
        self.name_kind = name_kind

    def __call__(
        self,
        value: t.Any,
        ctx: Context | None = None,
        param: Param | None = None,
    ) -> t.Any:
        if param and ctx:
            names = {
                "arg": param.argument_name,
                "param": param.param_name,
                "cli": param.cli_name,
            }
            origin = ctx.arg_origins[param.argument_name]
            ctx.logger.debug(
                f"{names.get(self.name_kind, param.argument_name)} = {value} ({origin.value})"
            )

        return value
