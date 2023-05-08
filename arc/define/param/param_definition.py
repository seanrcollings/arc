from __future__ import annotations

import collections
import inspect
import typing as t

from arc import api, errors, safe
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


class ParamDefinition(collections.deque[Param[t.Any]]):
    """A tree structure that represents how the parameters to a command look.
    This represents the definition of a command's paramaters, and not a particular
    execution of that comamnd with particular values"""

    BASE = "__arc_param_group_base"
    """A group with name `BASE` is the base group and
    gets spread into the function arguments"""

    def __init__(
        self,
        name: str,
        cls: type | None = None,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.cls: type | None = cls
        self.children: list[ParamDefinition] = []

    __repr__ = api.display("name", "data", "children")

    @property
    def is_base(self) -> bool:
        return self.name == self.BASE

    def all_params(self) -> t.Generator[Param[t.Any], None, None]:
        """Generator that yields all params in the tree"""
        yield from self

        if self.children:
            for child in self.children:
                yield from child.all_params()

    def create_instance(self) -> ParamTree[type[dict[str, t.Any]]]:
        return self.__create_param_instance(self)

    def __create_param_instance(self, definition: ParamDefinition) -> ParamTree[t.Any]:
        values: dict[str, ParamTree[t.Any] | ParamValue] = {
            param.argument_name: ParamValue(MISSING, param) for param in definition
        }

        for child in definition.children:
            values[child.name] = self.__create_param_instance(child)

        return ParamTree(
            values,
            definition.cls or dict,
        )


class ParamDefinitionFactory:
    def __init__(
        self,
        get_command_name: t.Callable[..., str],
        transform_snake_case: bool = True,
    ):
        self.param_names: set[str] = set()
        self.get_command_name = get_command_name
        self.transform_snake_case = transform_snake_case

    def from_function(self, func: t.Callable[..., t.Any]) -> ParamDefinition:
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
                        "Parameter groups cannot have a default value",
                        self.get_command_name(),
                        param,
                    )
                definition = self._from_param_group(param.annotation, param.name)
                root.children.append(definition)
            else:
                command_param = self.create_param(param)

                if command_param.short_name:
                    if len(command_param.short_name) > 1:
                        raise errors.ParamError(
                            f"Parameter {command_param.param_name}'s shortened name is longer than 1 character",
                            self.get_command_name(),
                            command_param,
                        )

                    if command_param.short_name in self.param_names:
                        raise errors.ParamError(
                            f"Parameter {command_param.param_name} shortened name "
                            f"{command_param.short_name!r} is non-unique.",
                            self.get_command_name(),
                        )

                if command_param.type.is_union_type:
                    for sub in command_param.type.sub_types:
                        if safe.issubclass(sub.origin, (set, tuple, list)):
                            raise errors.ParamError(
                                f"{command_param.type.original_type} is not a valid type. "
                                f"lists, sets, and tuples cannot be members of a Union / Optional type",
                                self.get_command_name(),
                            )

                root.append(command_param)

        return root

    def create_param(self, param: inspect.Parameter) -> Param[t.Any]:
        if param.name in self.param_names:
            raise errors.ParamError(
                f"Parameter name '{param.name}' is non-unique. "
                "All parameters for a given command must have a unique name",
                self.get_command_name(),
            )

        self.param_names.add(param.name)
        annotation = t.Any if param.annotation is param.empty else param.annotation
        type_info = TypeInfo[t.Any].analyze(annotation)
        info = self.get_param_info(param, type_info)

        annotation = param.annotation
        if annotation is param.empty:
            annotation = bool if info.param_cls is FlagParam else str

        if self.transform_snake_case and not info.param_name:
            info.param_name = param.name.replace("_", "-")

        return info.param_cls(
            argument_name=param.name,
            type=type_info,
            **info.dict(),
        )

    def get_param_info(
        self, param: inspect.Parameter, type_info: TypeInfo[t.Any]
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
                    "As such, it cannot be provided with a default value or parameter value",
                    self.get_command_name(),
                )
            info.callback = type_info.origin.__depends__

        return info

    def get_param_cls(
        self, param: inspect.Parameter, type_info: TypeInfo[t.Any]
    ) -> type[Param[t.Any]]:
        origin = type_info.origin

        if param.kind is param.POSITIONAL_ONLY:
            raise errors.ParamError(
                "Positional only arguments are not allowed. "
                "please remove the '/' from your function definition",
                self.get_command_name(),
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

    def _get_sig(self, obj: t.Callable[..., t.Any] | type) -> inspect.Signature:
        sig = inspect.signature(obj)
        annotations = t.get_type_hints(obj, include_extras=True)

        for param in sig.parameters.values():
            param._annotation = annotations.get(param.name, param.annotation)  # type: ignore

        return sig
