from __future__ import annotations
import inspect
import pprint
from types import FunctionType, MappingProxyType
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Protocol,
    get_type_hints,
    TYPE_CHECKING,
)
import abc

from arc import logging
from arc import errors
from arc.command.argument import Argument
from arc.utils import levenshtein
from arc.config import config
from arc.result import Err, Ok, Result
from arc.color import colorize, fg

from arc.types.helpers import join_and
from arc.callbacks.callback_store import CallbackStore
from arc.command.param_mixin import ParamMixin
from arc.command.param_builder import ParamBuilder

if TYPE_CHECKING:
    from arc.command.param import Param
    from arc.execution_state import ExecutionState
    from arc.parser import Parsed


logger = logging.getArcLogger("exe")

BAR = "―" * 40

# TODO: Consider moving a lot of this logic back into the Command class
# It doesn't really make sense here because the exectuable should just
# be concerned with how to call the underlying the object, which is a lot
# more than the object is doing

# TODO: Retreiving argument values shouldn't modify the Parsed object


class Executable(abc.ABC, ParamMixin):
    builder: type[ParamBuilder] = ParamBuilder
    state: ExecutionState

    def __init__(self, wrapped: Callable):
        super().__init__()
        self.wrapped = wrapped
        self.callback_store = CallbackStore()

        if config.mode == "development":
            self.params  # instantiate params for dev

    def __call__(self, state: ExecutionState):
        self.state = state
        self.state.executable = self
        parsed = self.state.parsed
        assert parsed is not None

        arguments = self.get_args()
        state.arguments = arguments
        self.exhastive_check(parsed)
        self.setup(arguments)

        try:
            logger.debug(BAR)
            result = self.run({key: arg.value for key, arg in arguments.items()})
            if not isinstance(result, (Ok, Err)):
                result = Ok(result)

        except BaseException as e:
            result = Err(e)
            raise
        finally:
            logger.debug(BAR)
            self.cleanup(result, arguments)

        return result

    @abc.abstractmethod
    def run(self, args: dict[str, Any]) -> Any:
        ...

    def get_args(self):
        # Construct the arguments dict, the final product of which
        # will be passed to the wrapped function or class
        arguments: dict[str, Argument] = {}
        for param in self.params.values():
            arg = param.get_arg(self.state)
            arg.pre_execute(self.state)
            arguments[param.arg_name] = arg

        return arguments

    def setup(self, arguments: dict[str, Argument]):
        logger.info("Arguments: %s", pprint.pformat(arguments))
        self.callback_store.pre_execution(
            {key: arg.value for key, arg in arguments.items()}
        )

    def cleanup(self, result: Result, arguments: dict[str, Argument]):
        self.callback_store.post_execution(result)
        for arg in arguments.values():
            arg.post_execute(result, self.state)

    def exhastive_check(self, parsed: Parsed):
        """Ensures that all arguments from the parser are handled"""
        if parsed["pos_values"]:

            pos_params_len = len(self.pos_params)
            raise errors.ArgumentError(
                f"{self.state.command_name} expects {pos_params_len} "
                f"positional argument{'s' if pos_params_len > 1 else ''}, "
                f"but recieved {pos_params_len + len(parsed['pos_values'])}"
            )

        if parsed["key_values"]:
            raise self.non_existant_args(list(parsed["key_values"].keys()))

    def non_existant_args(self, vals: list[str]):
        if len(vals) == 1:
            styled = colorize(config.flag_prefix + vals[0], fg.YELLOW)
            message = f"Option {styled} not recognized"
        else:
            styled = " ".join(
                colorize(config.flag_prefix + arg, fg.YELLOW) for arg in vals
            )
            message = f"Options {styled} not recognized"

        suggest_args = set(
            param.arg_alias
            for name in vals
            if (param := self.find_argument_suggestions(name)) is not None
        )

        if len(suggest_args) > 0:
            message += f"\n\tPerhaps you meant {colorize(join_and(list(suggest_args)), fg.YELLOW)}?"

        return errors.MissingArgError(message)

    def find_argument_suggestions(self, missing: str) -> Optional[Param]:
        visible_args = (self.key_params | self.flag_params).values()
        if config.suggest_on_missing_argument and len(visible_args) > 0:
            distance, arg = min(
                (
                    (levenshtein(param.arg_alias, missing), param)
                    for param in visible_args
                ),
                key=lambda tup: tup[0],
            )

            if distance <= config.suggest_levenshtein_distance:
                return arg

        return None


class FunctionExecutable(Executable):
    wrapped: FunctionType

    def run(self, args: dict[str, Any]):
        return self.wrapped(**args)


class WrappedClassExecutable(Protocol):
    def handle(self) -> Any:
        ...


class ClassExecutable(Executable):
    wrapped: type[WrappedClassExecutable]

    def __init__(self, wrapped: type[WrappedClassExecutable]):
        if not hasattr(wrapped, "handle"):
            raise errors.CommandError(
                f"Class-based commands must have a {colorize('handle()', fg.YELLOW)} method"
            )

        self.__build_class_params(wrapped)
        super().__init__(wrapped)

    def run(self, args: dict[str, Any]):
        instance = self.wrapped()
        for key, val in args.items():
            setattr(instance, key, val)

        return instance.handle()

    def __build_class_params(self, wrapped: type[WrappedClassExecutable]):
        sig = inspect.signature(wrapped)
        annotations = get_type_hints(wrapped, include_extras=True)
        defaults = {
            name: val for name, val in vars(wrapped).items() if name in annotations
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
        # to generate the correct signature object
        # during the paramater building process
        wrapped.__signature__ = sig  # type: ignore
