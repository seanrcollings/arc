from __future__ import annotations
from typing import Annotated, Optional, Any
from dataclasses import dataclass
from arc.command.param import ParamType, NO_DEFAULT


@dataclass
class Meta:
    name: Optional[str] = None
    type: Optional[ParamType] = None
    short: Optional[str] = None
    hidden: bool = False
    default: Any = NO_DEFAULT


def meta(**kwargs):
    def inner(cls: type):
        return Annotated[cls, Meta(**kwargs)]

    return inner
