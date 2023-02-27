from __future__ import annotations
import typing as t

from arc import constants

if t.TYPE_CHECKING:
    from arc.prompt.prompt import Prompt
    from arc.define.param.param import Param
    from arc.context import Context


def input_prompt(param: Param, ctx: Context, **kwargs) -> t.Any:
    default = constants.MISSING if param.default is not constants.MISSING else None
    return ctx.prompt.input(
        param.prompt_string,
        convert=param.type.original_type,
        default=default,
        **kwargs,
    )


def password_prompt(param: Param, ctx: Context):
    return input_prompt(param, ctx, echo=False)


def select_prompt(prompt: Prompt, string: str, values: list, **kwargs):
    res = prompt.select(string, values, **kwargs)

    if res is None:
        return constants.MISSING

    return res[1]
