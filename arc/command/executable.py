import inspect
from types import MappingProxyType
from typing import Protocol, Union, Any, Callable, cast
from typing_extensions import get_type_hints
from arc.command.arg_builder import ArgBuilder
from arc import errors
from arc.color import colorize, fg
from arc.command.argument import NO_DEFAULT
from arc.command import Context


class WrappedClassExecutable(Protocol):
    def __init__(self, **kwargs):
        ...

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

        if inspect.isfunction(wrapped):
            return FunctionExecutable(wrapped)
        else:
            wrapped = cast(type[WrappedClassExecutable], wrapped)
            return ClassExecutable(wrapped)

    def __init__(self, wrapped: WrappedExectuable):
        self.wrapped = wrapped
        self.args = self.build_args()

    def run(self, args: dict[str, Any]):
        ...

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

    def build_args(self, arg_aliases=None):
        with ArgBuilder(self.wrapped, arg_aliases) as builder:
            return builder.args


class FunctionExecutable(Executable):
    def run(self, args: dict[str, Any]):
        args = self.fill_defaults(args, {})
        self.verify_args_filled(args)
        return self.wrapped(**args)


class ClassExecutable(Executable):
    def __init__(self, wrapped: type[WrappedClassExecutable]):
        assert hasattr(wrapped, "handle")
        self.__build_class_params(wrapped)
        super().__init__(wrapped)

    def run(self, args: dict[str, Any]):
        args = self.fill_defaults(args, {})
        self.verify_args_filled(args)
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
