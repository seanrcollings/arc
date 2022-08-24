from __future__ import annotations
import typing as t
import inspect

from arc import errors, utils
from arc.config import config
from arc.constants import MISSING
from arc.types.type_info import TypeInfo
from .param import Action, InjectedParam, Param, FlagParam, ArgumentParam, OptionParam
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
        if param.default is not param.empty:
            raise errors.ParamError("Param groups cannot have a default value", param)

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
        # TODO: pass this type_info into the param, instead of creating it twice
        type_info = TypeInfo.analyze(param.annotation)
        info = self.get_param_info(param, type_info)

        annotation = param.annotation
        if annotation is param.empty:
            annotation = bool if info.param_cls is FlagParam else str

        if config.transform_snake_case and not info.param_name:
            info.param_name = param.name.replace("_", "-")

        return info.param_cls(
            argument_name=param.name,
            annotation=annotation,
            **info.dict(),
        )

    def get_param_info(
        self, param: inspect.Parameter, type_info: TypeInfo
    ) -> ParamInfo:
        if isinstance(param.default, ParamInfo):
            info = param.default
        else:
            info = ParamInfo(
                param_cls=self.get_param_cls(param, type_info),
                default=param.default if param.default is not param.empty else MISSING,
            )

        if hasattr(type_info.origin, "__depends__"):
            if param.default is not param.empty:
                raise errors.ParamError(
                    f"type {param.annotation} is a special type used for dependancy injection. "
                    "As such, it cannot be provided with a default value or parameter value"
                )
            info.callback = type_info.origin.__depends__

        return info

    def get_param_cls(
        self, param: inspect.Parameter, type_info: TypeInfo
    ) -> type[Param]:
        origin = type_info.origin

        if param.kind is param.POSITIONAL_ONLY:
            raise errors.ParamError(
                "Positional only arguments are not allowed. "
                "please remove the '/' from your function definition",
                param,
            )

        if hasattr(origin, "__depends__"):
            return InjectedParam
        elif origin is bool or isinstance(param.default, bool):
            return FlagParam
        elif param.kind is param.KEYWORD_ONLY:
            return OptionParam
        else:
            return ArgumentParam
