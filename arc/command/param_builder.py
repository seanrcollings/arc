from __future__ import annotations
from types import MappingProxyType
from typing import get_type_hints, get_args, TYPE_CHECKING
import inspect

from arc import errors
from arc.command.param import Param, Meta, VarKeyword, VarPositional
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
            if argument.kind in (argument.VAR_KEYWORD, argument.VAR_POSITIONAL):
                raise errors.ArgumentError(
                    "Arc does not support *args and **kwargs. "
                    "Please use their typed counterparts VarPositional and KeyPositional"
                )

            annotation = self.annotations.get(argument.name, str)
            if is_annotated(annotation):
                # TODO : Make sure meta is of type Meta()
                annotation, meta = get_args(argument.annotation)
            else:
                meta = Meta()

            argument._annotation = annotation  # type: ignore # pylint: disable=protected-access

            param = Param(argument, meta)

            # Type checks
            if annotation is VarPositional:
                self.__executable.var_pos_param = param
            elif annotation is VarKeyword:
                self.__executable.var_key_param = param
            elif safe_issubclass(annotation, Context):
                param.hidden = True

            params[param.arg_alias] = param

        shorts = [param.short for param in params.values() if param.short]
        if len(shorts) != len(set(shorts)):
            raise errors.ArgumentError(
                "A Command's short argument names must be unique"
            )

        return params


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

        params = {
            name: inspect.Parameter(
                name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=defaults.get(name, inspect.Parameter.empty),
                annotation=annotation,
            )
            for name, annotation in annotations.items()
        }

        # pylint: disable=protected-access
        sig._parameters = MappingProxyType(params)  # type: ignore
        executable.__signature__ = sig  # type: ignore
