from __future__ import annotations
from types import MappingProxyType
from typing import Any, Callable, Optional, get_type_hints, TYPE_CHECKING
import inspect
import functools


from arc import errors, logging, constants
from arc.config import config
from arc.color import colorize, fg
from arc._command import param
from arc.types.params import ParamInfo
from arc.typing import ClassCallback

if TYPE_CHECKING:
    from arc._command.param import Param

logger = logging.getArcLogger("prb")


class ParamBuilder:
    def __init__(self, func: Callable):
        self.sig = inspect.signature(func)
        self.annotations = get_type_hints(func, include_extras=True)

    def build(self):
        params: list[Param] = []
        for arg in self.sig.parameters.values():
            arg._annotation = self.annotations.get(arg.name) or str

            if arg.kind in (arg.VAR_KEYWORD, arg.VAR_POSITIONAL):
                raise errors.ArgumentError("Arc does not support *args and **kwargs.")
            if isinstance(arg.default, ParamInfo):
                info: ParamInfo = arg.default
            else:
                info = ParamInfo(
                    default=arg.default
                    if arg.default is not arg.empty
                    else constants.MISSING,
                )

            # By default, snake_case args are transformed to kebab-case
            # for the command line. However, this can be ignored
            # by declaring an explicit name in the ParamInfo
            # or by setting the config value to false
            if config.transform_snake_case and not info.arg_alias:
                info.arg_alias = arg.name.replace("_", "-")

            should_negotiate_param_type = self.param_type_override(arg, info)
            if should_negotiate_param_type:
                self.negotiate_param_type(arg, info)

            param_obj = info.param_cls(
                arg_name=arg.name,
                annotation=arg.annotation,
                **info.dict(),
            )

            params.append(param_obj)

        shorts = [param.short for param in params if param.short]
        if len(shorts) != len(set(shorts)):
            raise errors.ArgumentError(
                "A Command's short argument names must be unique"
            )

        return params

    def negotiate_param_type(self, arg: inspect.Parameter, info: ParamInfo):
        if not info.param_cls:
            if arg.annotation is bool:
                info.param_cls = param.Flag
                if info.default is constants.MISSING:
                    info.default = False

            elif arg.kind is arg.POSITIONAL_ONLY:
                raise errors.ArgumentError(
                    "Positional only arguments are not allowed as arc "
                    "passes all arguments by keyword internally "
                    f"please remove the {colorize('/', fg.YELLOW)} from "
                    "your function definition",
                )
            elif arg.kind is arg.KEYWORD_ONLY:
                info.param_cls = param.Option
            elif arg.kind is arg.POSITIONAL_OR_KEYWORD:
                info.param_cls = param.Argument

    def param_type_override(self, arg: inspect.Parameter, info: ParamInfo):
        """Data types can contain info in a `__param_info__` class variable.

        if `__param_info__['overwrite']`, is `False`: each item in there will
        overide any user-declared values of `info`.

        if it is True, the user properties will overwrite the type properties
        when the user properties are not `None` or `constants.MISSING`
        """
        default_values = (constants.MISSING, None)
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


def wrap_class_callback(cls: type[ClassCallback]) -> Callable[..., Any]:
    """Function to wrap class callbacks in a function callback equivalent to:
    1. Creating an instance of the class
    2. Adding each argument as an attribute of the instance
    3. calling `instance.handle()`
    """
    sig = inspect.signature(cls)
    annotations = get_type_hints(cls, include_extras=True)
    defaults = {name: val for name, val in vars(cls).items() if name in annotations}

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

    def wrapper(**kwargs):
        instance = cls()
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance.handle()

    functools.update_wrapper(wrapper, cls)
    # inspect.signature() checks for a cached signature object
    # at __signature__. So we can cache it there
    # to generate the correct signature object
    # during the parameter building process
    cls.__signature__ = sig  # type: ignore
    wrapper.__signature__ = sig  # type: ignore
    return wrapper
