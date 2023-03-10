from __future__ import annotations

import collections
import inspect
import typing as t

from arc import api, errors
from arc import typing as at
from arc.constants import MISSING
from arc.define import classful
from arc.define.param import groups
from arc.define.param.constructors import ParamInfo
from arc.define.param.param import (
    ArgumentParam,
    FlagParam,
    InjectedParam,
    OptionParam,
    Param,
)
from arc.define.param.param_tree import ParamTree, ParamValue
from arc.types.type_info import TypeInfo


class ParamDefinition(collections.UserList[Param]):
    """A tree structure that represents how the parameters to a command look.
    This represents the definition of a command's paramaters, and not a particular
    execution of that comamnd with particular values"""

    BASE = "__arc_param_group_base"
    """A group with name `BASE` is the base group and
    gets spread into the function arguments"""

    def __init__(self, name: str, cls: type | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.cls: type | None = cls
        self.children: list[ParamDefinition] = []

    __repr__ = api.display("name", "data", "children")

    @property
    def is_base(self) -> bool:
        return self.name == self.BASE

    def all_params(self) -> t.Generator[Param, None, None]:
        """Generator that yields all params in the tree"""
        yield from self.data

        if self.children:
            for child in self.children:
                yield from child.all_params()

    def create_instance(self) -> ParamTree:
        return self.__create_param_instance(self)

    def __create_param_instance(self, definition: ParamDefinition) -> ParamTree:
        values: dict[str, ParamTree | ParamValue] = {
            param.argument_name: ParamValue(MISSING, param)
            for param in definition
            # if param.expose
        }

        for child in definition.children:
            values[child.name] = self.__create_param_instance(child)

        return ParamTree(
            values,
            definition.cls or dict,
        )


class ParamDefinitionFactory:
    def __init__(self, transform_snake_case: bool = True):
        self.param_names: set[str] = set()
        self.transform_snake_case = transform_snake_case

    def from_function(self, func: t.Callable) -> ParamDefinition:
        self.param_names.clear()
        sig = self._get_sig(func)
        return self.build(sig)

    def from_class(self, cls: type) -> ParamDefinition:
        self.param_names.clear()
        sig = classful.class_signature(cls)
        return self.build(sig)

    def _from_param_group(self, cls: type, name: str) -> ParamDefinition:
        definition = groups.get_cached_definition(cls)

        if not definition:
            options = t.cast(at.ParamGroupOptions, groups.groupoptions(cls))
            sig = classful.class_signature(cls)
            definition = self.build(sig, exclude=options["exclude"])
            definition.name = name
            definition.cls = cls
            groups.cache_definition(cls, definition)

        return definition

    def build(
        self, sig: inspect.Signature, exclude: t.Sequence[str] | None = None
    ) -> ParamDefinition:
        exclude = exclude or []
        root = ParamDefinition(ParamDefinition.BASE)

        iterable = (
            param for param in sig.parameters.values() if param.name not in exclude
        )
        for param in iterable:
            if groups.isgroup(param.annotation):
                if param.default is not param.empty:
                    raise errors.ParamError(
                        "Parameter groups cannot have a default value", param
                    )
                definition = self._from_param_group(param.annotation, param.name)
                root.children.append(definition)
            else:
                root.append(self.create_param(param))

        return root

    def create_param(self, param: inspect.Parameter) -> Param:
        if param.name in self.param_names:
            raise errors.ParamError(
                f"Parameter name '{param.name}' is non-unique. "
                "All parameters for a given command must have a unique name"
            )

        self.param_names.add(param.name)
        # TODO: pass this type_info into the param, instead of creating it twice
        type_info = TypeInfo.analyze(param.annotation)
        info = self.get_param_info(param, type_info)

        annotation = param.annotation
        if annotation is param.empty:
            annotation = bool if info.param_cls is FlagParam else str

        if self.transform_snake_case and not info.param_name:
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

    def _get_sig(self, obj: t.Callable | type) -> inspect.Signature:
        sig = inspect.signature(obj)
        annotations = t.get_type_hints(obj, include_extras=True)

        for param in sig.parameters.values():
            param._annotation = annotations.get(param.name, param.annotation)  # type: ignore

        return sig
