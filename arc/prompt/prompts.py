from __future__ import annotations

import typing as t

from arc import constants

if t.TYPE_CHECKING:
    from arc.define.param.param import Param
    from arc.prompt.prompt import Prompt
    from arc.runtime import Context


def input_prompt(param: Param[t.Any], ctx: Context, **kwargs: t.Any) -> t.Any:
    default = (
        constants.MISSING_DEFAULT
        if param.default is constants.MISSING
        else constants.MISSING
    )
    return ctx.prompt.input(
        param.prompt_string,
        convert=param.type.original_type,
        default=default,
        **kwargs,
    )


def select_prompt(
    prompt: Prompt, string: str, values: list[str], **kwargs: t.Any
) -> t.Any:
    res = prompt.select(string, values, **kwargs)

    if res is None:
        return constants.MISSING

    return res[1]
