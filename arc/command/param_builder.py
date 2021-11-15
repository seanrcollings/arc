from __future__ import annotations
import logging
from types import MappingProxyType
from typing import Any, Optional, get_type_hints, TYPE_CHECKING
import inspect

from arc import errors
from arc.config import config
from arc.color import colorize, fg
from arc.command import param
from arc.types.params import ParamInfo

if TYPE_CHECKING:
    from arc.command.executable import Executable

logger = logging.getLogger("arc_logger")


class ParamBuilder:
    def __init__(self, executable: Executable):
        self.sig = inspect.signature(executable.wrapped)
        self.annotations = get_type_hints(executable.wrapped, include_extras=True)

    def build(self):
        params: dict = {}
        for arg in self.sig.parameters.values():
            arg._annotation = self.annotations.get(arg.name) or str

            if arg.kind in (arg.VAR_KEYWORD, arg.VAR_POSITIONAL):
                raise errors.ArgumentError(
                    "Arc does not support *args and **kwargs. "
                    f"Please use their typed counterparts "
                    f"{colorize('arc.VarPositional', fg.ARC_BLUE)} "
                    f"and {colorize('arc.VarKeyword', fg.ARC_BLUE)}"
                )

            if isinstance(arg.default, ParamInfo):
                info: ParamInfo = arg.default
            else:
                info = self.create_param_info(arg)

            should_negotiate_param_type = self.param_type_override(arg, info)
            if should_negotiate_param_type:
                self.negotiate_param_type(arg, info)

            param_obj = info.param_cls(
                arg_name=arg.name,
                annotation=arg.annotation,
                arg_alias=info.name,
                short=info.short,
                default=info.default,
                description=info.description,
            )

            params[param_obj.arg_alias] = param_obj

        shorts = [param.short for param in params.values() if param.short]
        if len(shorts) != len(set(shorts)):
            raise errors.ArgumentError(
                "A Command's short argument names must be unique"
            )

        return params

    def create_param_info(self, arg: inspect.Parameter) -> ParamInfo:
        info = ParamInfo(
            name=arg.name,
            default=arg.default if arg.default is not arg.empty else param.MISSING,
        )

        # By default, snake_case args are transformed to kebab-case
        # for the command line. However, this can be ignored
        # by declaring an explicit name in the Meta()
        # or by setting the config value to false
        if config.transform_snake_case:
            info.name = arg.name.replace("_", "-")

        return info

    def negotiate_param_type(self, arg: inspect.Parameter, info: ParamInfo):
        if not info.param_cls:
            if arg.annotation is bool:
                info.param_cls = param.FlagParam
                if info.default is param.MISSING:
                    info.default = False

            elif arg.kind is arg.POSITIONAL_ONLY:
                raise errors.ArgumentError(
                    "Positional only arguments are not allowed as arc "
                    "passes all arguments by keyword internally"
                    f"please remove the {colorize('/', fg.YELLOW)} from",
                    "your function definition",
                )
            elif arg.kind is arg.KEYWORD_ONLY:
                info.param_cls = param.KeywordParam
            elif arg.kind is arg.POSITIONAL_OR_KEYWORD:
                info.param_cls = param.PositionalParam

    def param_type_override(self, arg: inspect.Parameter, info: ParamInfo):
        """Data types can contain info in a `__param_info__` class variable.

        if `__param_info__['overwrite']`, is `False`: each item in there will
        overide any user-declared values of `info`.

        if it is True, the user properties will overwrite the type properties
        when the user properties are not `None` or `param.MISSING`
        """
        default_values = (param.MISSING, None)
        type_param_info: Optional[dict[str, Any]] = getattr(
            arg.annotation, "__param_info__", None
        )
        should_negotiate_param_type = True

        if type_param_info:
            overwrite = type_param_info.pop("overwrite", False)
            for name, value in type_param_info.items():
                curr = getattr(info, name)

                if overwrite:
                    if curr in default_values:
                        setattr(info, name, value)

                elif value not in default_values:
                    if name == "param_cls":
                        should_negotiate_param_type = False
                    if curr not in default_values and curr != value:
                        # TODO: improve this error message
                        raise errors.ArgumentError(
                            f"Param type {colorize(arg.annotation.__name__, fg.YELLOW)} does "
                            f"not allow modification of the {colorize(name, fg.YELLOW)} property"
                        )

                    setattr(info, name, value)

        return should_negotiate_param_type
