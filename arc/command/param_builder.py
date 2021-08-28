from __future__ import annotations
from types import MappingProxyType
from typing import get_type_hints, get_args, TYPE_CHECKING
import inspect

from arc import errors
from arc.command.param import (
    NO_DEFAULT,
    Param,
    Meta,
    ParamType,
    VarKeyword,
    VarPositional,
)
from arc.command.context import Context
from arc.types import is_annotated, safe_issubclass

if TYPE_CHECKING:
    from arc.command.executable import Executable


class ParamBuilder:
    def __init__(self, executable: Executable):
        self.__executable: Executable = executable
        self.sig = inspect.signature(executable.wrapped)
        self.annotations = get_type_hints(executable.wrapped, include_extras=True)

    def build(self):
        params = {}
        for argument in self.sig.parameters.values():
            self.argument_hook(argument)
            annotation, meta = self.unwrap_type(
                self.annotations.get(argument.name, str)
            )
            argument._annotation = annotation  # type: ignore # pylint: disable=protected-access

            param = Param(argument, meta)
            self.param_hook(param)

            params[param.arg_alias] = param

        shorts = [param.short for param in params.values() if param.short]
        if len(shorts) != len(set(shorts)):
            raise errors.ArgumentError(
                "A Command's short argument names must be unique"
            )

        return params

    def argument_hook(self, _arg: inspect.Parameter):
        ...

    def param_hook(self, param: Param):
        if param.annotation is VarPositional:
            self.__executable.var_pos_param = param
        elif param.annotation is VarKeyword:
            self.__executable.var_key_param = param
        elif safe_issubclass(param.annotation, Context):
            param.hidden = True

    def unwrap_type(self, kind: type):
        if is_annotated(kind):
            # TODO : Make sure meta is of type Meta()
            args = get_args(kind)
            assert len(args) == 2
            assert isinstance(args[1], Meta)
            kind, meta = args
        else:
            meta = Meta()

        return kind, meta


class FunctionParamBuilder(ParamBuilder):
    def argument_hook(self, arg: inspect.Parameter):
        if arg.kind in (arg.VAR_KEYWORD, arg.VAR_POSITIONAL):
            raise errors.ArgumentError(
                "Arc does not support *args and **kwargs. "
                "Please use their typed counterparts VarPositional and KeyPositional"
            )


class ClassParamBuilder(ParamBuilder):
    def __init__(self, executable: Executable):
        self.__build_class_params(executable.wrapped)
        super().__init__(executable)

    def __build_class_params(self, executable):
        sig = inspect.signature(executable)
        annotations = get_type_hints(executable, include_extras=True)
        defaults = {
            name: val for name, val in vars(executable).items() if name in annotations
        }

        sig._parameters = MappingProxyType(  # type: ignore # pylint: disable=protected-access
            {
                name: inspect.Parameter(
                    name=name,
                    kind=inspect.Parameter.KEYWORD_ONLY
                    if (default := defaults.get(name, inspect.Parameter.empty))
                    is not inspect.Parameter.empty
                    else inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=default,
                    annotation=annotation,
                )
                for name, annotation in annotations.items()
            }
        )

        # inspect.signature() checks for a cached signature object
        # at __signature__. So we can cache it there
        # to generate the correct signature object for
        # self.build()
        executable.__signature__ = sig  # type: ignore
