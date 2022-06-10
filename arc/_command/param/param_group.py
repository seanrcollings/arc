from __future__ import annotations
import typing as t
import collections

from py import process
from arc.constants import MISSING

import arc.typing as at
from .param import Param

if t.TYPE_CHECKING:
    from arc.context import Context


class ParamGroup(collections.UserList[Param]):
    DEFAULT = "default"
    sub_groups: list[ParamGroup]

    def __init__(self, name: str, cls: type | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.cls = cls
        self.sub_groups = []

    def __repr__(self):
        return f"ParamGroup(name={self.name!r}, params={self.data!r})"

    def all_params(self):
        """Generator that yields all params in itself, and in it's sub groups recursivley"""
        if self.sub_groups:
            for sub in self.sub_groups:
                yield from sub.all_params()

        yield from self.data

    @property
    def is_default(self) -> bool:
        return self.name == self.DEFAULT

    @classmethod
    def get_default_group(cls, groups: list[ParamGroup]) -> ParamGroup | None:
        for group in groups:
            if group.is_default:
                return group

        return None

    def process_parsed_result(
        self, res: at.ParseResult, ctx: Context
    ) -> tuple[t.Any | dict, list[Param]]:
        processed = {}
        missing: list[Param] = []

        param: Param
        for param in self.data:
            if param.is_injected:
                continue

            value = param.process_parsed_result(res, ctx)
            if value is MISSING:
                missing.append(param)
            processed[param.argument_name] = value

        for sub in self.sub_groups:
            processed[sub.name], sub_missing = sub.process_parsed_result(res, ctx)
            missing.extend(sub_missing)

        if self.cls:
            inst = self.cls()
            for key, value in processed.items():
                setattr(inst, key, value)

            return (inst, missing)

        return processed, missing

    def inject_dependancies(self, args: dict[str, t.Any], ctx: Context):
        injected = {}

        for param in self:
            if not param.is_injected:
                continue

            injected[param.argument_name] = (
                param.callback(ctx) if param.callback else None
            )

        if self.sub_groups:
            inst = args[self.name]
            for sub in self.sub_groups:
                sub.inject_dependancies({sub.name: getattr(inst, sub.name)}, ctx)

        if self.cls:
            inst = args[self.name]
            for key, value in injected.items():
                setattr(inst, key, value)

        args.update(injected)
