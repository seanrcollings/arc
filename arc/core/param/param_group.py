from __future__ import annotations
import typing as t
import collections

from arc.constants import MISSING
from arc import errors
import arc.typing as at
from .param import InjectedParam, Param

if t.TYPE_CHECKING:
    from arc.context import Context


class ParamGroup(collections.UserList[Param]):
    DEFAULT = "default"
    """A group with name `DEFAULT` is the base group and
    gets spread into the function arguments"""
    sub_groups: list[ParamGroup]

    def __init__(self, name: str, cls: type | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.cls = cls
        self.sub_groups = []

    def __repr__(self):
        return f"ParamGroup(name={self.name!r}, params={self.data!r})"

    def all_params(self) -> t.Generator[Param, None, None]:
        """Generator that yields all params in itself, and in it's sub groups recursivley"""
        yield from self.data

        if self.sub_groups:
            for sub in self.sub_groups:
                yield from sub.all_params()

    @property
    def is_default(self) -> bool:
        return self.name == self.DEFAULT

    @classmethod
    def get_default_group(cls, groups: list[ParamGroup]) -> ParamGroup:
        for group in groups:
            if group.is_default:
                return group

        raise errors.InternalError("No default param group found")

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
            if param.expose:
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

            param = t.cast(InjectedParam, param)

            value = param.get_injected_value(ctx)
            injected[param.argument_name] = value

        if self.sub_groups:
            inst = args[self.name]
            for sub in self.sub_groups:
                sub.inject_dependancies({sub.name: getattr(inst, sub.name)}, ctx)

        if self.cls:
            inst = args[self.name]
            for key, value in injected.items():
                setattr(inst, key, value)
        else:
            args.update(injected)
