from __future__ import annotations
import types
import typing as t
import dataclasses as dc

from arc import errors

if t.TYPE_CHECKING:
    from arc.context import Context
    from arc._command import Command


DecoratorFunc = t.Callable[["Context"], t.Optional[t.Generator[None, t.Any, None]]]


@dc.dataclass(frozen=True)
class CommandDecorator:
    name: str
    func: DecoratorFunc
    inherit: bool = True

    def __call__(self, command: Command) -> Command:
        command.decorators.add(self)
        return command

    def remove(self, command: Command) -> Command:
        """Removes the callback from the decorated `command`"""
        command.decorators.remove(self)
        return command


def decorator(
    func: DecoratorFunc = None, *, inherit: bool = True
) -> t.Callable[[DecoratorFunc], CommandDecorator]:
    """Decorator that transforms the decorated function into a arc decorator"""

    def inner(func: DecoratorFunc):
        return CommandDecorator(
            name=func.__name__,
            func=func,
            inherit=inherit,
        )

    if func:
        return inner(func)

    return inner


def remove(*decos: CommandDecorator) -> t.Callable[[Command], Command]:
    """Decorator that removes all `*decos` from the decorated `command`"""

    def inner(command: Command) -> Command:
        for dc in decos:
            dc.remove(command)

        return command

    return inner


ErrorHandlerFunc = t.Callable[[Exception, "Context"], None]


def error_handler(*errors: type[Exception], inherit: bool = False):
    from arc.context import Context

    def inner(func: ErrorHandlerFunc):
        def handle_errors(_ctx):
            try:
                yield
            except errors as e:
                func(e, Context.current())

        return CommandDecorator(
            name=func.__name__,
            func=handle_errors,
            inherit=inherit,
        )

    return inner


class DecoratorStack:
    __decos: list[CommandDecorator]
    __gens: list[t.Generator[None, t.Any, None]]

    def __repr__(self):
        return f"DecoratorStack({self.__decos})"

    def __init__(self):
        self.__decos = []
        self.__gens = []

    def __iter__(self):
        yield from self.__decos

    def __contains__(self, value):
        return value in self.__decos

    def start(self, ctx: Context):
        for deco in reversed(self.__decos):
            gen = deco.func(ctx)  # type: ignore
            if isinstance(gen, types.GeneratorType):
                next(gen)
                self.__gens.append(gen)  # type: ignore

    def close(self):
        """Closes each callback by calling `next()` on them"""
        for gen in reversed(self.__gens):
            try:
                next(gen)
            except StopIteration:
                ...

    def add(self, deco: CommandDecorator):
        self.__decos.append(deco)

    def remove(self, deco: CommandDecorator):
        self.__decos.remove(deco)

    def throw(self, exception: Exception):
        """Used if an error occurs in command execution.
        Notifies each of the callbacks that an error occured.

        Args:
            exception: The exception that occured within the executing command

        Raises:
            exception: if none of the callbacks handle the exception, re-raises
        """

        exc_type = type(exception)
        trace = exception.__traceback__

        exception_handled = False

        for gen in reversed(self.__gens):
            try:
                if exception_handled:
                    try:
                        next(gen)
                    except StopIteration:
                        ...
                else:
                    gen.throw(exc_type, exception, trace)
            except StopIteration:
                exception_handled = True
            except Exception as e:
                if isinstance(e, errors.Exit):
                    raise e

                exception = e

        if not exception_handled:
            raise exception
