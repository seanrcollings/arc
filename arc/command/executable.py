import pprint
from typing import Any, Callable, Optional, Protocol
import logging
import abc

from arc import errors
from arc.utils import levenshtein
from arc.config import config
from arc.result import Err, Ok
from arc.color import colorize, fg
from arc.command.param import Param
from arc.execution_state import ExecutionState
from arc.command.argument_parser import Parsed
from arc.types.helpers import join_and
from arc.callbacks.callback_store import CallbackStore
from arc.command.param_mixin import ParamMixin
from arc.command.param_builder import (
    ClassParamBuilder,
    FunctionParamBuilder,
    ParamBuilder,
)

logger = logging.getLogger("arc_logger")

BAR = "―" * 40


class Executable(abc.ABC, ParamMixin):
    builder: type[ParamBuilder]
    state: ExecutionState

    def __init__(self, wrapped: Callable):
        super().__init__()
        self.wrapped = wrapped
        self.callback_store = CallbackStore()

    def __call__(self, state: ExecutionState):
        # Setup
        self.state = state
        self.state.executable = self
        parsed = self.state.parsed
        assert parsed is not None

        # Construct the arguments dict, the final product of which
        # will be passed to the wrapped function or class
        arguments: dict[str, Any] = {}
        for param in self.params.values():
            value = param.default
            value = param.run_hooks(value, self.state)
            arguments[param.arg_name] = value

        self.exhastive_check(parsed)

        logger.debug("Function Arguments: %s", pprint.pformat(arguments))

        self.callback_store.pre_execution(arguments)
        logger.debug(BAR)

        try:
            result = self.run(arguments)
            if not isinstance(result, (Ok, Err)):
                result = Ok(result)
        except BaseException:
            # TODO: add more descriptive error message here
            result = Err("Execution failed")
            raise
        finally:
            logger.debug(BAR)
            self.callback_store.post_execution(result)

        return result

    @abc.abstractmethod
    def run(self, args: dict[str, Any]) -> Any:
        ...

    def exhastive_check(self, parsed: Parsed):
        """Ensures that all arguments from the parser are handled"""
        if parsed["pos_args"]:
            raise errors.ArgumentError("Too many positional arguments")

        if parsed["options"]:
            raise self.non_existant_args(parsed["options"])

        if parsed["flags"]:
            raise errors.ArgumentError("Too many flags!")

    def get_or_raise(self, key: str, message):
        arg = self.params.get(key)
        if arg and not arg.hidden:
            return arg

        for arg in self.params.values():
            if key == arg.short and not arg.hidden:
                return arg

        raise errors.MissingArgError(message, name=key)

    def non_existant_args(self, vals: dict[str, str]):
        missing_args = [key for key in vals if key not in self.key_params]
        if len(missing_args) == 1:
            styled = colorize(config.flag_denoter + missing_args[0], fg.YELLOW)
            message = f"Option {styled} does not exist"
        else:
            styled = " ".join(
                colorize(config.flag_denoter + arg, fg.YELLOW) for arg in missing_args
            )
            message = f"Options {styled} do not exist"

        suggest_args = set(
            param.arg_alias
            for name in missing_args
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
    builder = FunctionParamBuilder

    def run(self, args: dict[str, Any]):
        return self.wrapped(**args)


class WrappedClassExecutable(Protocol):
    def handle(self) -> Any:
        ...


class ClassExecutable(Executable):
    builder = ClassParamBuilder
    wrapped: type[WrappedClassExecutable]

    def __init__(self, wrapped: type[WrappedClassExecutable]):
        if not hasattr(wrapped, "handle"):
            raise errors.CommandError(
                f"Class-based commands must have a {colorize('handle()', fg.YELLOW)} method"
            )

        super().__init__(wrapped)

    def run(self, args: dict[str, Any]):
        instance = self.wrapped()
        for key, val in args.items():
            setattr(instance, key, val)

        return instance.handle()
