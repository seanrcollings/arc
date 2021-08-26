import pprint
from typing import Any, Callable, Optional, Protocol, get_args, get_type_hints
from types import MappingProxyType
import inspect
import logging
import abc

from arc import errors
from arc.config import config
from arc.result import Err, Ok
from arc.color import colorize, fg
from arc.command.argument_parser import Parsed
from arc.command.context import Context
from arc.command.param import Meta, Param, VarKeyword, VarPositional, NO_DEFAULT
from arc.execution_state import ExecutionState
from arc.types import convert
from arc.types.helpers import is_annotated, safe_issubclass
from arc.callbacks.callback_store import CallbackStore

logger = logging.getLogger("arc_logger")

BAR = "―" * 40


class Executable(abc.ABC):
    state: ExecutionState
    # Params aren't constructed until
    # a command is actually executed
    _params: dict[str, Param] = {}

    _pos_params: dict[str, Param] = {}
    _key_params: dict[str, Param] = {}
    _flag_params: dict[str, Param] = {}
    _optional_params: dict[str, Param] = {}
    _required_params: dict[str, Param] = {}
    _hidden_params: dict[str, Param] = {}

    var_pos_param: Optional[Param] = None
    var_key_param: Optional[Param] = None

    def __init__(self, wrapped: Callable):
        self.wrapped = wrapped
        self.callback_store = CallbackStore()

    def __call__(self, parsed: Parsed, state: ExecutionState):
        self.state = state
        arguments: dict[str, Any] = {}
        arguments |= self.handle_postional(parsed["pos_args"])
        arguments |= self.handle_keyword(parsed["options"])
        arguments |= self.handle_flags(parsed["flags"])
        arguments |= self.handle_hidden()

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

    @property
    def params(self):
        if not self._params:
            self._params = self.build_params()

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

    @abc.abstractmethod
    def run(self, args: dict[str, Any]) -> Any:
        ...

    def handle_postional(self, vals: list[str]) -> dict[str, Any]:
        pos_args: dict[str, Any] = {}

        for idx, param in enumerate(self.pos_params.values()):
            if idx > len(vals) - 1:
                if param.default is not NO_DEFAULT:
                    value = param.default
                else:
                    raise errors.ArgumentError("Too few positional arguments")
            else:
                value = convert(vals[idx], param.annotation, param.arg_alias)

            pos_args[param.arg_name] = value

        self.handle_var_positional(pos_args, vals)

        return pos_args

    def handle_var_positional(self, pos_args: dict[str, Any], vals: list[str]):

        # TODO provide type conversion to all values here
        if len(vals) > len(self.pos_params):
            if not self.var_pos_param:
                raise errors.ArgumentError(
                    f"{colorize(self.state.command_name, fg.ARC_BLUE)} "
                    f"expects {len(self.pos_params)} positional arguments, "
                    f"but recieved {len(vals)}"
                )

            pos_args[self.var_pos_param.arg_name] = vals[len(self.pos_params) :]
        elif self.var_pos_param:
            pos_args[self.var_pos_param.arg_name] = []

    def handle_keyword(self, vals: dict[str, str]) -> dict[str, Any]:
        vals = vals.copy()
        keyword_args: dict[str, Any] = {}

        if not self.var_key_param and not all(val in self.key_params for val in vals):
            raise self.missing_key_args(vals)

        for key, param in self.key_params.items():

            if value := vals.get(key):
                vals.pop(key)
            elif value := vals.get(param.short):
                vals.pop(param.short)
            else:
                value = param.default

            if value is NO_DEFAULT:
                raise errors.ArgumentError(f"No value for required argument {key}")

            if value is not param.default:
                value = convert(value, param.annotation, key)

            keyword_args[param.arg_name] = value

        if self.var_key_param:
            self.handle_var_keyword(keyword_args, vals)

        return keyword_args

    def handle_var_keyword(self, keyword_args: dict[str, Any], vals: dict[str, str]):
        assert self.var_key_param
        if len(vals) > len(self.key_params):
            keyword_args[self.var_key_param.arg_name] = {
                key: val for key, val in vals.items() if key not in self.key_params
            }
        else:
            keyword_args[self.var_key_param.arg_name] = {}

    def handle_flags(self, vals: list[str]) -> dict[str, bool]:
        vals = vals.copy()
        flag_args: dict[str, bool] = {}

        for key, param in self.flag_params.items():
            if key in vals:
                vals.remove(key)
                flag_args[param.arg_name] = not param.default
            elif param.short in vals:
                vals.remove(param.short)
                flag_args[param.arg_name] = not param.default
            else:
                flag_args[param.arg_name] = param.default

        if len(vals) > 0:
            # TODO: improve error
            raise errors.ArgumentError(f"Flag(s) {vals} not recognized")

        return flag_args

    def handle_hidden(self):
        hidden_args: dict[str, Any] = {}

        for name, param in self.hidden_params.items():
            if safe_issubclass(param.annotation, Context):
                hidden_args[name] = param.annotation(self.state.context)

        return hidden_args

    def build_params(self):
        sig = inspect.signature(self.wrapped)
        annotations = get_type_hints(self.wrapped, include_extras=True)
        params = {}

        for argument in sig.parameters.values():
            # TODO: provide a more helpful error here than an assertion error
            assert argument.kind not in (argument.VAR_KEYWORD, argument.VAR_POSITIONAL)

            annotation = annotations.get(argument.name, str)
            if is_annotated(annotation):
                # TODO : Make sure meta is of type Meta()
                annotation, meta = get_args(argument.annotation)
            else:
                meta = Meta()

            argument._annotation = annotation  # type: ignore # pylint: disable=protected-access

            param = Param(argument, meta)

            # Type checks
            if annotation is VarPositional:
                self.var_pos_param = param
            elif annotation is VarKeyword:
                self.var_key_param = param
            elif safe_issubclass(annotation, Context):
                param.hidden = True

            params[param.arg_alias] = param

        shorts = [param.short for param in params.values() if param.short]
        if len(shorts) != len(set(shorts)):
            raise errors.ArgumentError(
                "A Command's short argument names must be unique"
            )

        return params

    def get_or_raise(self, key: str, message):
        arg = self.params.get(key)
        if arg and not arg.hidden:
            return arg

        for arg in self.params.values():
            if key == arg.short and not arg.hidden:
                return arg

        raise errors.MissingArgError(message, name=key)

    def missing_key_args(self, vals: dict[str, str]):
        missing_args = [key for key in vals if key not in self.key_params]
        if len(missing_args) == 1:
            styled = colorize(config.flag_denoter + missing_args[0], fg.YELLOW)
            message = f"Option {styled} not recognized"
        else:
            styled = " ".join(
                colorize(config.flag_denoter + arg, fg.YELLOW) for arg in missing_args
            )
            message = f"Options {styled} not recognized"

        return errors.MissingArgError(message)


class FunctionExecutable(Executable):
    def run(self, args: dict[str, Any]):
        return self.wrapped(**args)


class WrappedClassExecutable(Protocol):
    def handle(self) -> Any:
        ...


class ClassExecutable(Executable):
    wrapped: type[WrappedClassExecutable]

    def __init__(self, wrapped: type[WrappedClassExecutable]):
        assert hasattr(
            wrapped, "handle"
        ), f"Class-based commands must have a {colorize('handle()', fg.YELLOW)} method"

        self.__build_class_params(wrapped)
        super().__init__(wrapped)

    def run(self, args: dict[str, Any]):
        instance = self.wrapped()
        for key, val in args.items():
            setattr(instance, key, val)

        return instance.handle()

    def __build_class_params(self, executable: type[WrappedClassExecutable]):
        sig = inspect.signature(executable)
        annotations = get_type_hints(executable, include_extras=True)
        defaults = {
            name: val
            for name, val in vars(executable).items()
            if not name.startswith("__") and name != "handle"
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
