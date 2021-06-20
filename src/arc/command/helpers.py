from __future__ import annotations
import inspect
from typing import Dict, Any, TYPE_CHECKING, Callable, get_type_hints
import functools
import textwrap

from arc.errors import CommandError, ExecutionError, NoOpError
from arc import utils
from arc.color import fg, effects

from .argument import Argument, NO_DEFAULT, EMPTY
from .context import Context

if TYPE_CHECKING:
    from .command import Command


class CommandMixin:
    args: Dict[str, Argument]
    context: Dict[str, Any]

    def assert_args_filled(self):
        for option in self.args.values():
            if option.value is NO_DEFAULT:
                raise CommandError(f"No value for required option '{option.name}'")


class ParamProxy:
    def __init__(self, param: inspect.Parameter, annotation: type):
        self.param = param
        self.annotation = annotation

    def __getattr__(self, name):
        return getattr(self.param, name)


class ArgBuilder:
    def __init__(self, function):
        self.__annotations = get_type_hints(function)
        self.__sig = inspect.signature(function)
        self.__length = len(self.__sig.parameters.values())
        self.__args: Dict[str, Argument] = {}
        self.__hidden_args: Dict[str, Argument] = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self

    def __len__(self):
        return self.__length

    def __iter__(self):
        for param in self.__sig.parameters.values():
            proxy = ParamProxy(param, self.__annotations.get(param.name, str))
            yield proxy
            self.add_arg(proxy)

    @property
    def args(self):
        return self.__args

    @property
    def hidden_args(self):
        return self.__hidden_args

    def add_arg(self, param: ParamProxy):

        if param.annotation is bool:
            default = False if param.default is EMPTY else param.default
            self.__args[param.name] = Argument(param.name, param.annotation, default)

        elif param.kind not in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
            self.__args[param.name] = Argument(
                param.name, param.annotation, param.default
            )

    def get_meta(self, **kwargs):
        return dict(length=self.__length, **kwargs)
