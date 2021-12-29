from __future__ import annotations
import typing as t
import dataclasses as dc


if t.TYPE_CHECKING:
    from arc.context import Context
    from arc._command import Command


CallbackFunc = t.Callable[[dict[str, t.Any], "Context"], t.Generator[None, t.Any, None]]


@dc.dataclass(frozen=True)
class Callback:
    name: str
    func: CallbackFunc
    inherit: bool = True

    def __call__(self, command: Command) -> Command:
        command.callbacks.add(self)
        return command

    def remove(self, command: Command) -> Command:
        """Removes the callback from the decorated `command`"""
        command.callbacks.remove(self)
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
        gen.send(None)  # Advance it to the first yield
        self.__stack.append(gen)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        for gen in reversed(self.__stack):
            try:
                if exc_value:
                    gen.throw(exc_type, exc_value, trace)
                else:
                    gen.send(None)
            except StopIteration:
                ...

    def close(self, exception: Exception = None):
        if exception:
            exc_type: t.Optional[type[Exception]] = type(exception)
            trace = exception.__traceback__
        else:
            exc_type = None
            trace = None

        self.__exit__(exc_type, exception, trace)
