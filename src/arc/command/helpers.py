from __future__ import annotations
import inspect
from typing import Dict, Any, TYPE_CHECKING, Callable, get_type_hints
import functools
import textwrap

from arc.errors import CommandError, ExecutionError, NoOpError
from arc import utils
from arc.color import fg, effects

from .__option import Option, NO_DEFAULT, EMPTY
from .context import Context

if TYPE_CHECKING:
    from .command import Command


class CommandMixin:
    args: Dict[str, Option]
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
        self.__args: Dict[str, Option] = {}
        self.__hidden_args: Dict[str, Option] = {}

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
        if Context in param.annotation.mro():
            self.__hidden_args["context"] = Option(
                param.name, param.annotation, NO_DEFAULT
            )

        elif param.annotation is bool:
            default = False if param.default is EMPTY else param.default
            self.__args[param.name] = Option(param.name, param.annotation, default)

        elif param.kind not in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
            self.__args[param.name] = Option(
                param.name, param.annotation, param.default
            )

    def get_meta(self, **kwargs):
        return dict(length=self.__length, **kwargs)


class FunctionWrapper:
    """Wraps the function associated with a command

    The value returned by __get__ is also a form of wrapper,
    so this wrapper is a wrapper around a wrapper.
    While this may seem strange at first, there are a
    couple of advantages to this approach:

    1. Abstracts away the setup post function
    assignment (setting up arguments, doc string, etc...).
    This means that anytime `command.function` is set,
    the related setup will also be ran.

    2. Because we return a wrapped version of the function
    (using `@functools.wraps()`) it appears to the outside world
    to be the original function. However, when called, we can do some
    extra magic before and after the call that the caller doesn't need
    to know about. Currently it times the function call, prints out some
    debug information, and wraps the call in try / catch block for
    NoOpError and Execution Error
    """

    def __get__(self, command: Command, objtype=None):
        return self.wrapper(command._function, command)

    def __set__(self, command: Command, value: Callable):
        command._function = value
        self.__post_set(command)

    def __post_set(self, command: Command):
        """Intilization that relates to the command's wrapped function
        This init must be called each time the function is set
        """

        args: tuple = command.build_args()
        command.args = args[0]
        command._hidden_args = args[1]  # pylint: disable=protected-access

        command.doc = None
        if (doc := command.function.__doc__) is not None:
            command.doc = textwrap.dedent(doc)

    def wrapper(self, function, command: Command):
        """Actually where a command's function executes
        provides some wrapping functionality around the function
        call"""

        @functools.wraps(function)
        @utils.timer("Command Execution")
        def wrapper(*args, **kwargs):
            BAR = "\u2500" * 40
            try:
                utils.logger.debug(BAR)
                return function(*args, **kwargs, **command.hidden_args)
            except NoOpError as e:
                print(
                    fg.RED + "This namespace cannot be executed. "
                    f"Check '[...]:{command.name}:help' for possible subcommands"
                    + effects.CLEAR
                )
            except ExecutionError as e:
                print(e)
            finally:
                utils.logger.debug(BAR)

        return wrapper
