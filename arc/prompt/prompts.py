from __future__ import annotations
import typing as t

import arc
from arc.prompt import select
from arc import constants

if t.TYPE_CHECKING:
    from arc.prompt.prompt import Prompt
    from arc.core.param.param import Param
    from arc.context import Context


def input_prompt(prompt: Prompt, param: Param, **kwargs):
    empty = param.default is not constants.MISSING

    return prompt.input(param.prompt_string, empty=empty, **kwargs) or constants.MISSING


def password_prompt(prompt: Prompt, param: Param):
    return input_prompt(prompt, param, sensitive=True)


def select_prompt(values: list, config, param: Param, **kwargs):
    arc.print(param.prompt)
    res = select(values, highlight_color=config.brand_color, **kwargs)

    if res is None:
        return constants.MISSING

    return res[1]
