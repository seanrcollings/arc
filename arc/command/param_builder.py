from __future__ import annotations
from types import MappingProxyType
from typing import get_type_hints, get_args, TYPE_CHECKING
import inspect
import dataclasses
import copy

from arc.types import is_annotated, Meta
from arc import errors
from arc.config import config
from arc.color import colorize, fg
from arc.command.param import Param
from arc.types.params import MISSING, ParamType

if TYPE_CHECKING:
    from arc.command.executable import Executable


class ParamBuilder:
    def __init__(self, executable: Executable):
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

            meta = self.build_meta(argument, meta)
            meta_dict = dataclasses.asdict(meta)
            meta_dict["arg_alias"] = meta_dict.pop("name")

            param = Param(
                arg_name=argument.name,
                annotation=annotation,
                **meta_dict,
            )
            self.param_hook(param)

            params[param.arg_alias] = param

        shorts = [param.short for param in params.values() if param.short]
        if len(shorts) != len(set(shorts)):
            raise errors.ArgumentError(
                "A Command's short argument names must be unique"
            )

        return params

    def build_meta(self, arg: inspect.Parameter, meta: Meta):
        # By default, snake_case args are transformed to kebab-case
        # for the command line. However, this can be ignored
        # by declaring an explicit name in the Meta()
        # or by setting the config value to false
        if not meta.name:
            meta.name = (
                arg.name.replace("_", "-") if config.tranform_snake_case else arg.name
            )

        if meta.default is MISSING and arg.default is not arg.empty:
            meta.default = arg.default

        if not meta.type:
            if arg.annotation is bool:
                meta.type = ParamType.FLAG
                if meta.default is MISSING:
                    meta.default = False
            elif arg.kind is arg.POSITIONAL_ONLY:
                raise errors.ArgumentError(
                    "Positional only arguments are not allowed as arc "
                    "passes all arguments by keyword internally"
                    f"please remove the {colorize('/', fg.YELLOW)} from",
                    "your function definition",
                )
            elif arg.kind is arg.KEYWORD_ONLY:
                meta.type = ParamType.KEY
            elif arg.kind is arg.POSITIONAL_OR_KEYWORD:
                meta.type = ParamType.POS

        return meta

    def argument_hook(self, _arg: inspect.Parameter):
        ...

    def param_hook(self, _param: Param):
        ...

    def unwrap_type(self, kind: type):
        if is_annotated(kind):
            args = get_args(kind)
            assert len(args) >= 2
            kind = args[0]
            metas: tuple[Meta, ...] = args[1:]
        else:
            metas = (Meta(),)

        # Make a copy of user_meta rather than editing user_meta directly
        # because instances may be attached to a type definition
        # (i.e: Context, VarPositional) which will cause subsequent
        # usages of a type to behave differently
        merged = copy.copy(metas[0])
        for meta in metas[1:]:
            data = dataclasses.asdict(meta)
            for name, value in data.items():
                if name == "hooks":
                    merged.hooks.extend(value)
                elif value != Meta.__dataclass_fields__.get(name).default:  # type: ignore # pylint: disable=no-member
                    setattr(merged, name, value)

        return kind, merged


class FunctionParamBuilder(ParamBuilder):
    def argument_hook(self, arg: inspect.Parameter):
        if arg.kind in (arg.VAR_KEYWORD, arg.VAR_POSITIONAL):
            raise errors.ArgumentError(
                "Arc does not support *args and **kwargs. "
                f"Please use their typed counterparts {colorize('arc.VarPositional', fg.ARC_BLUE)} "
                f"and {colorize('arc.VarKeyword', fg.ARC_BLUE)}"
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
