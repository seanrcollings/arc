from __future__ import annotations
import typing as t

import arc
from arc.prompt import select
from arc import constants

if t.TYPE_CHECKING:
    from arc._command.param.param import Param
    from arc.context import Context


def input_prompt(ctx: Context, param: Param, **kwargs):
    empty = param.default is not constants.MISSING

    return (
        ctx.prompt.input(param.prompt_string, empty=empty, **kwargs)
        or constants.MISSING
    )


def password_prompt(ctx: Context, param: Param):
    return input_prompt(ctx, param, sensitive=True)


def select_prompt(values: list, ctx: Context, param: Param, **kwargs):
    arc.print(param.prompt)
    res = select(values, highlight_color=ctx.config.brand_color, **kwargs)

    if res is None:
        return constants.MISSING

    return res[1]
