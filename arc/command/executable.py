import inspect
from types import MappingProxyType, MethodType, FunctionType
from typing import Protocol, Union, Any, Callable, cast, get_type_hints

from arc.result import Err, Ok, Result
from arc.execution_state import ExecutionState
from arc.command.arg_builder import ArgBuilder
from arc import errors
from arc.color import colorize, fg
from arc.command.argument import NO_DEFAULT
from arc.command.context import Context


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
        self.build_args(short_args)

    def run(self, args: dict[str, Any], state: ExecutionState) -> Result:
        args = self.fill_defaults(args, state.context)
        self.verify_args_filled(args)
        result = self.call(args)

        if not isinstance(result, (Ok, Err)):
            return Ok(result)
        return result

    def call(self, _args: dict[str, Any]) -> Result:
        return Err("Not a valid call")

    def fill_defaults(self, args: dict[str, Any], context: dict[str, Any]):
        unfilled = {}
        for key, arg in self.args.items():
            if key not in args:
                try:
                    if issubclass(arg.annotation, Context):
                        unfilled[key] = arg.annotation(context)
                    else:
                        unfilled[key] = arg.default
                except TypeError:
                    unfilled[key] = arg.default

        return args | unfilled

    def verify_args_filled(self, arguments: dict):
        for key, value in arguments.items():
            if value is NO_DEFAULT:
                raise errors.ValidationError(
                    f"No value provided for argument: {colorize(key, fg.YELLOW)}",
                )

    def build_args(self, short_args=None):
        with ArgBuilder(self.wrapped, short_args) as builder:
            self.args = builder.args


class FunctionExecutable(Executable):
    wrapped: Callable

    def call(self, args: dict[str, Any]):
        return self.wrapped(**args)


class ClassExecutable(Executable):
    wrapped: type[WrappedClassExecutable]

    def __init__(self, wrapped: type[WrappedClassExecutable], *args, **kwargs):
        assert hasattr(wrapped, "handle")
        self.__build_class_params(wrapped)
        super().__init__(wrapped, *args, **kwargs)

    def call(self, args: dict[str, Any]):
        instance = self.wrapped()
        for name, value in args.items():
            setattr(instance, name, value)
        return instance.handle()

    def __build_class_params(self, executable: type[WrappedClassExecutable]):
        sig = inspect.signature(executable)
        annotations = get_type_hints(executable)
        defaults = {
            name: val
            for name, val in vars(executable).items()
            if not name.startswith("__") and name != "handle"
        }

        params = {
            name: inspect.Parameter(
                name,
                inspect.Parameter.KEYWORD_ONLY,
                default=defaults.get(name, inspect.Parameter.empty),
                annotation=annotation,
            )
            for name, annotation in annotations.items()
        }
        # pylint: disable=protected-access
        sig._parameters = MappingProxyType(params)  # type: ignore
        executable.__signature__ = sig  # type: ignore
