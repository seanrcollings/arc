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
from arc.types.params import MISSING
from arc.execution_state import ExecutionState
from arc.command.argument_parser import Parsed
from arc.types import convert
from arc.types.helpers import join_and
from arc.callbacks.callback_store import CallbackStore
from arc.command.param_builder import (
    ClassParamBuilder,
    FunctionParamBuilder,
    ParamBuilder,
)

logger = logging.getLogger("arc_logger")

BAR = "―" * 40


class ParamMixin:
    builder: type[ParamBuilder]
    # Params aren't constructed until
    # a command is actually executed
    _params: Optional[dict[str, Param]] = None

    _pos_params: dict[str, Param] = {}
    _key_params: dict[str, Param] = {}
    _flag_params: dict[str, Param] = {}
    _optional_params: dict[str, Param] = {}
    _required_params: dict[str, Param] = {}
    _hidden_params: dict[str, Param] = {}
    _var_pos_param: Optional[Param] = MISSING  # type: ignore
    _var_key_param: Optional[Param] = MISSING  # type: ignore

    @property
    def params(self):
        if self._params is None:
            self._params = self.builder(self).build()

        return self._params

    @property
    def pos_params(self):
        if not self._pos_params:
            self._pos_params = {
                key: param
                for key, param in self.params.items()
                if param.is_positional and not param.hidden
            }
        return self._pos_params

    @property
    def key_params(self):
        if not self._key_params:
            self._key_params = {
                key: param
                for key, param in self.params.items()
                if param.is_keyword and not param.hidden
            }
        return self._key_params

    @property
    def flag_params(self):
        if not self._flag_params:
            self._flag_params = {
                key: param
                for key, param in self.params.items()
                if param.is_flag and not param.hidden
            }
        return self._flag_params

    @property
    def optional_params(self):
        if not self._optional_params:
            self._optional_params = {
                key: param
                for key, param in self.params.items()
                if param.optional and not param.hidden
            }
        return self._optional_params

    @property
    def required_params(self):
        if not self._required_params:
            self._required_params = {
                key: param
                for key, param in self.params.items()
                if not param.optional and not param.hidden
            }
        return self._required_params

    @property
    def hidden_params(self):
        if not self._hidden_params:
            self._hidden_params = {
                key: param for key, param in self.params.items() if param.hidden
            }
        return self._hidden_params


class Executable(abc.ABC, ParamMixin):
    builder: type[ParamBuilder]
    state: ExecutionState

    def __init__(self, wrapped: Callable):
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
        arguments |= self.handle_postional(parsed["pos_args"])
        arguments |= self.handle_keyword(parsed["options"])
        arguments |= self.handle_flags(parsed["flags"])
        arguments |= self.handle_hidden()
        self.handle_extra(parsed)

        logger.debug("Function Arguments: %s", pprint.pformat(arguments))

        self.callback_store.pre_execution(arguments)
        logger.debug(BAR)

        try:
            result = self.run(arguments)
            if not isinstance(result, (Ok, Err)):
                result = Ok(result)
        except Exception:
            result = Err("Execution failed")
            raise
        finally:
            logger.debug(BAR)
            self.callback_store.post_execution(result)

        return result

    @abc.abstractmethod
    def run(self, args: dict[str, Any]) -> Any:
        ...

    def handle_postional(self, vals: list[str]) -> dict[str, Any]:
        pos_args: dict[str, Any] = {}

        for idx, param in reversed(list(enumerate(self.pos_params.values()))):
            if idx > len(vals) - 1:
                if param.default is not MISSING:
                    value = param.default
                else:
                    raise errors.ArgumentError(
                        "No value provided for required positional argument: "
                        + colorize(param.arg_alias, fg.YELLOW)
                    )
            else:
                value = vals.pop(idx)
                value = convert(value, param.annotation, param.arg_alias)

            value = param.run_hooks(value, self.state)
            pos_args[param.arg_name] = value

        return pos_args

    def handle_keyword(self, vals: dict[str, str]) -> dict[str, Any]:
        keyword_args: dict[str, Any] = {}

        for key, param in self.key_params.items():
            if value := vals.get(key):
                vals.pop(key)
            elif value := vals.get(param.short):
                vals.pop(param.short)
            else:
                value = param.default

            if value is MISSING:
                raise errors.ArgumentError(
                    "No value provided for required option: "
                    + colorize(config.flag_denoter + key, fg.YELLOW)
                )

            if value is not param.default:
                value = convert(value, param.annotation, key)

            value = param.run_hooks(value, self.state)
            keyword_args[param.arg_name] = value

        return keyword_args

    def handle_flags(self, vals: list[str]) -> dict[str, bool]:
        flag_args: dict[str, bool] = {}

        # TODO : This is a O(n^2) algorithm
        # improve to O(n) by turning parsed['flags']
        # into a set
        for key, param in self.flag_params.items():
            if key in vals:
                vals.remove(key)
                value = not param.default
            elif param.short in vals:
                vals.remove(param.short)
                value = not param.default
            else:
                value = param.default

            value = param.run_hooks(value, self.state)
            flag_args[param.arg_name] = value

        return flag_args

    def handle_hidden(self):
        hidden_args: dict[str, Any] = {}

        for name, param in self.hidden_params.items():
            value = param.default
            value = param.run_hooks(value, self.state)
            hidden_args[name] = value

        return hidden_args

    def handle_extra(self, parsed: Parsed):
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
