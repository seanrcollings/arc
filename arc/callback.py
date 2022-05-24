from __future__ import annotations
import types
import typing as t
import dataclasses as dc

from arc import errors

if t.TYPE_CHECKING:
    from arc.context import Context
    from arc._command import Command


CallbackFunc = t.Callable[[dict[str, t.Any], "Context"], t.Generator[None, t.Any, None]]

ErrorHandlerFunc = t.Callable[[Exception, "Context"], t.Optional[bool]]


@dc.dataclass(frozen=True)
class Callback:
    name: str
    func: CallbackFunc
    inherit: bool = True

    def __call__(self, command: Command) -> Command:
        command.callbacks.append(self)
        return command

    def remove(self, command: Command) -> Command:
        """Removes the callback from the decorated `command`"""
        command.removed_callbacks.append(self)
        return command


def create(
    func: CallbackFunc = None, *, inherit: bool = True
) -> t.Callable[[CallbackFunc], Callback]:
    """Decorator that transforms the decorated function into a callback"""

    def inner(func: CallbackFunc):
        return Callback(
            name=func.__name__,
            func=func,
            inherit=inherit,
        )

    if func:
        return inner(func)

    return inner


def remove(*callbacks: Callback) -> t.Callable[[Command], Command]:
    """Decorator that removes all `*callbacks` from the decorated `command`"""

    def inner(command: Command) -> Command:
        for cb in callbacks:
            cb.remove(command)

        return command

    return inner


class CallbackStack:
    __stack: list[t.Generator[None, t.Any, None]]

    def __repr__(self):
        return f"CallbackStore({self.__stack})"

    def __init__(self):
        self.__stack = []

    def add(self, gen: t.Generator[None, t.Any, None]):
        if not isinstance(gen, types.GeneratorType):
            raise errors.CallbackError("Callback must be a generator.")
        next(gen)  # Advance it to the first yield
        self.__stack.append(gen)

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

        for gen in reversed(self.__stack):
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

    def close(self):
        """Closes each callback by calling `next()` on them"""
        for gen in reversed(self.__stack):
            try:
                next(gen)
            except StopIteration:
                ...
