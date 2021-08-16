from __future__ import annotations
import inspect
from types import MappingProxyType, MethodType, FunctionType
from typing import (
    Optional,
    Protocol,
    Union,
    Any,
    Callable,
    cast,
    get_type_hints,
    NewType,
    TYPE_CHECKING,
)
import pprint
import logging

from arc.result import Err, Ok, Result
from arc.execution_state import ExecutionState
from arc.command.arg_builder import ArgBuilder
from arc import errors
from arc.color import colorize, fg
from arc.command.argument import NO_DEFAULT, Argument
from arc.command.context import Context


if TYPE_CHECKING:
    from arc.command.argument_parser import Parsed

logger = logging.getLogger("arc_logger")
BAR = "\u2500" * 40


class WrappedClassExecutable(Protocol):
    def handle(self) -> Any:
        ...


WrappedExectuable = Union[type[WrappedClassExecutable], Callable]


class Executable:
    """Wrapper around executable objects"""

    def __new__(cls, wrapped: WrappedExectuable, *args, **kwargs):
        if cls in (FunctionExecutable, ClassExecutable):
            obj = object.__new__(cls)
            obj.__init__(wrapped, *args, **kwargs)
            return obj

        if isinstance(wrapped, (MethodType, FunctionType)):
            return FunctionExecutable(wrapped, *args, **kwargs)
        else:
            wrapped = cast(type[WrappedClassExecutable], wrapped)
            return ClassExecutable(wrapped, *args, **kwargs)

    def __init__(self, wrapped: WrappedExectuable, short_args: dict[str, str]):
        self.wrapped = wrapped
        self.pass_args = False
        self.pass_kwargs = False
        self.build_args(short_args)
        self._pos_args: list[Argument] = []
        self._flags: list[Argument] = []
        self._options: list[Argument] = []
        self._visible: list[Argument] = []
        self._hidden: list[Argument] = []

    def run(self, args: Parsed, state: ExecutionState) -> Result:
        self.fill_defaults(args)
        self.fill_hidden(args, state)
        self.verify_args_filled(args)
        logger.debug("Function Arguments: %s", pprint.pformat(args))
        logger.debug(BAR)
        result = self.call(args)
        logger.debug(BAR)

        if not isinstance(result, (Ok, Err)):
            return Ok(result)
        return result

    def setup(self, args: Parsed, state: ExecutionState):
        """Perform pre-execution setup"""

    def call(self, _args: Parsed) -> Result:
        return Err("Not a valid call")

    ### Helpers ###

    @property
    def pos_args(self):
        if not self._pos_args:
            self._pos_args = [
                arg
                for arg in self.args.values()
                if arg.is_positional() and not arg.hidden
            ]
        return self._pos_args

    @property
    def keyword_args(self):
        if not self._options:
            self._options = [
                arg for arg in self.args.values() if arg.is_keyword() and not arg.hidden
            ]
        return self._options

    @property
    def flag_args(self):
        if not self._flags:
            self._flags = [
                arg for arg in self.args.values() if arg.is_flag() and not arg.hidden
            ]
        return self._flags

    @property
    def hidden_args(self):
        if not self._hidden:
            self._hidden = [arg for arg in self.args.values() if arg.hidden]
        return self._hidden

    @property
    def visible_args(self):
        if not self._visible:
            self._visible = [arg for arg in self.args.values() if not arg.hidden]
        return self._visible

    def fill_defaults(self, args: Parsed):
        if len(self.pos_args) > len(args["pos_args"]):
            args["pos_args"] += [
                arg.default
                for arg in self.pos_args[
                    len(self.pos_args) - len(args["pos_args"]) - 1 :
                ]
            ]

        args["options"] = {
            key: arg.default for key, arg in self.args.items() if arg.is_keyword()
        } | args["options"]

        args["flags"] = {
            arg.name: args["flags"][arg.name]
            if arg.name in args["flags"]
            else arg.default
            for arg in self.flag_args
        }

    def fill_hidden(self, args: Parsed, state: ExecutionState):
        hidden = {}
        for arg in self.hidden_args:
            if issubclass(arg.annotation, Context):
                hidden[arg.name] = arg.annotation(state.context)

        args["options"] |= hidden

    def get_or_raise(self, key: str, message):
        key = key.replace("-", "_")
        arg = self.args.get(key)
        if arg and not arg.hidden:
            return arg

        for arg in self.args.values():
            if key == arg.short and not arg.hidden:
                return arg

        raise errors.MissingArgError(message, name=key)

    ### Validators ###
    def verify_args_filled(self, arguments: Parsed):
        for _, values in arguments.items():
            if isinstance(values, dict):
                for argname, argvalue in values.items():
                    if argvalue is NO_DEFAULT:
                        raise errors.ValidationError(
                            f"No value provided for argument: {colorize(argname, fg.YELLOW)}"
                        )

            else:
                values = cast(list, values)
                for idx, argvalue in enumerate(values):
                    if argvalue is NO_DEFAULT:
                        arg = self.pos_args[idx]
                        raise errors.ValidationError(
                            f"No value provided for argument: {colorize(arg.name, fg.YELLOW)}"
                        )

    ### Setup ###
    def build_args(self, short_args=None):
        with ArgBuilder(self.wrapped, short_args) as builder:
            for param in builder:
                if param.kind is param.VAR_KEYWORD:
                    self.pass_kwargs = True
                elif param.kind is param.VAR_POSITIONAL:
                    self.pass_args = True

            self.args = builder.args


class FunctionExecutable(Executable):
    wrapped: Callable

    def call(self, args: Parsed):
        return self.wrapped(
            *args["pos_args"],
            **args["options"],
            **args["flags"],
        )


VarPositional = NewType("VarPositional", list)
VarKeyword = NewType("VarKeyword", dict)

kind_mapping = {
    VarPositional: inspect.Parameter.VAR_POSITIONAL,
    VarKeyword: inspect.Parameter.VAR_KEYWORD,
}


class ClassExecutable(Executable):
    wrapped: type[WrappedClassExecutable]

    def __init__(self, wrapped: type[WrappedClassExecutable], *args, **kwargs):
        assert hasattr(wrapped, "handle")

        self.var_pos_args_name: Optional[str] = None
        self.var_keyword_args_name: Optional[str] = None

        self.__build_class_params(wrapped)
        super().__init__(wrapped, *args, **kwargs)

    def call(self, args: Parsed):
        instance = self.wrapped()

        for idx, value in enumerate(args["pos_args"][0 : len(self.pos_args)]):
            arg = self.pos_args[idx]
            setattr(instance, arg.name, value)

        if self.var_pos_args_name:
            setattr(
                instance,
                self.var_pos_args_name,
                args["pos_args"][len(self.pos_args) :],
            )

        class_level = {
            key: val
            for key, val in (args["options"] | args["flags"]).items()
            if key in self.args
        }

        for name, value in class_level.items():
            setattr(instance, name, value)

        if self.var_keyword_args_name:
            var_keyword = {
                key: val
                for key, val in (args["options"] | args["flags"]).items()
                if key not in self.args
            }
            setattr(instance, self.var_keyword_args_name, var_keyword)

        return instance.handle()

    def __build_class_params(self, executable: type[WrappedClassExecutable]):
        sig = inspect.signature(executable)
        annotations = get_type_hints(executable)
        defaults = {
            name: val
            for name, val in vars(executable).items()
            if not name.startswith("__") and name != "handle"
        }

        params: dict[str, inspect.Parameter] = {}
        for name, annotation in annotations.items():
            if annotation is VarPositional:
                self.var_pos_args_name = name
            elif annotation is VarKeyword:
                self.var_keyword_args_name = name

            params[name] = inspect.Parameter(
                name,
                kind_mapping.get(annotation, inspect.Parameter.KEYWORD_ONLY),
                default=defaults.get(name, inspect.Parameter.empty),
                annotation=annotation,
            )

        # pylint: disable=protected-access
        sig._parameters = MappingProxyType(params)  # type: ignore
        executable.__signature__ = sig  # type: ignore
