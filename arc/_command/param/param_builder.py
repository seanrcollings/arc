from __future__ import annotations
import typing as t
import inspect

from arc import errors, utils
from arc.constants import MISSING
from .param import Param, FlagParam, ArgumentParam, OptionParam
from .param_group import ParamGroup
from arc.params import ParamInfo


class ParamBuilder:
    def __init__(self, obj: t.Callable | type):
        self.sig = inspect.signature(obj)
        annotations = t.get_type_hints(obj, include_extras=True)
        for param in self.sig.parameters.values():
            param._annotation = annotations.get(param.name, param.annotation)  # type: ignore

    def build(self) -> list[ParamGroup]:
        groups: list[ParamGroup] = []
        default_group = ParamGroup(ParamGroup.DEFAULT)
        groups.append(default_group)

        for param in self.sig.parameters.values():
            if utils.isgroup(param.annotation):
                groups.append(self.build_param_group(param))
            else:
                default_group.append(self.create_param(param))

        return groups

    def build_param_group(self, param: inspect.Parameter) -> ParamGroup:
        if isinstance(param.default, ParamInfo):
            raise errors.ParamError("Canot define ParamInfo here", param)

        cls = param.annotation
        if hasattr(cls, "__param_group__"):
            return getattr(cls, "__param_group__")

        param_groups = type(self)(cls).build()
        default = param_groups[0]
        default.name = param.name
        default.cls = param.annotation
        default.sub_groups = param_groups[1:]
        setattr(cls, "__param_group__", default)
        return default

    def create_param(self, param: inspect.Parameter) -> Param:
        info = self.get_param_info(param)

        annotation = param.annotation
        if annotation is param.empty:
            annotation = bool if info.param_cls is FlagParam else str

        return info.param_cls(
            argument_name=param.name,
            annotation=annotation,
            **info.dict(),
        )

    def get_param_info(self, param: inspect.Parameter) -> ParamInfo:
        if isinstance(param.default, ParamInfo):
            info = param.default
            param_cls = info.param_cls
        else:
            param_cls = self.get_param_cls(param)
            info = ParamInfo(
                param_cls,
                default=param.default if param.default is not param.empty else MISSING,
            )

        # A default of false is always assumed with flags, so they
        # are always optional
        if info.default is MISSING and param_cls is FlagParam:
            info.default = False

        return info

    def get_param_cls(self, param: inspect.Parameter) -> type[Param]:
        if param.annotation is bool:
            return FlagParam

        elif param.kind is param.POSITIONAL_ONLY:
            raise errors.ParamError(
                "Positional only arguments are not allowed as arc "
                "passes all arguments by keyword internally "
                "please remove the '/' from "
                "your function definition",
                param,
            )

        elif param.kind is param.KEYWORD_ONLY:
            return OptionParam
        else:
            return ArgumentParam
