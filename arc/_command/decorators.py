from __future__ import annotations
import types
import typing as t
import dataclasses as dc

from arc import errors, utils

if t.TYPE_CHECKING:
    from arc.context import Context
    from arc._command import Command


D = t.TypeVar("D", bound=t.Callable)
E = t.TypeVar("E", bound=t.Callable)


class DecoratorMixin(t.Generic[D, E]):
    def __init__(self) -> None:
        self._decorators: list[Decorator[D] | Decorator[E]] = []
        self._removed_decorators: set[Decorator[D] | Decorator[E]] = set()

    def decorate(self, inherit: bool = True) -> t.Callable[[D], Decorator[D]]:
        def inner(func: D) -> Decorator[D]:
            deco: Decorator[D] = decorator(inherit=inherit)(func)
            self.add_decorator(deco)
            return deco

        return inner

    def handle(
        self, *errors: type[Exception], inherit: bool = False
    ) -> t.Callable[[E], Decorator]:
        from arc.context import Context

        def inner(func: E):
            def handle_errors(_ctx) -> t.Generator[None, None, None]:
                try:
                    yield
                except errors as e:
                    utils.dispatch_args(func, e, Context.current())

            deco: Decorator = Decorator(
                name=func.__name__,
                func=handle_errors,  # type: ignore
                inherit=inherit,
            )
            self.add_decorator(deco)
            return deco

        return inner

    def add_decorator(self, deco: Decorator[D]) -> None:
        self._decorators.append(deco)

    def remove_decorator(self, deco: Decorator[D]) -> None:
        self._removed_decorators.add(deco)

    @classmethod
    def create_decostack(
        cls, objs: t.Sequence[DecoratorMixin[D, E]]
    ) -> DecoratorStack[D | E]:
        """Creates a decorator stack for the current object, taking into account all of the
        decorators in the list of objects, and of what decorators have been removed
        in things higher in the list"""

        stack: DecoratorStack = DecoratorStack()
        last = objs[-1]
        for obj in objs:
            for added in obj._decorators:
                if added.inherit or obj is last:
                    stack.add(added)

            # TODO: Non optimal, is going to run in O(n^2).
            for removed in obj._removed_decorators:
                try:
                    stack.remove(removed)
                except ValueError:
                    ...

        return stack


class DecoratorStack(t.Generic[D]):
    __decos: list[Decorator[D]]
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
            gen = utils.dispatch_args(deco.func, ctx)  # type: ignore
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

    def add(self, deco: Decorator[D]):
        self.__decos.append(deco)

    def remove(self, deco: Decorator[D]):
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


A = t.TypeVar("A", bound=DecoratorMixin)


@dc.dataclass(frozen=True)
class Decorator(t.Generic[D]):
    name: str
    func: D
    inherit: bool = True

    def __call__(self, command: A) -> A:
        command.add_decorator(self)
        return command

    def remove(self, command: A) -> A:
        """Removes the callback from the decorated `command`"""
        command.remove_decorator(self)
        return command


def decorator(inherit: bool = True) -> t.Callable[[D], Decorator[D]]:
    """Decorator that transforms the decorated function into a arc decorator"""

    def inner(func: D) -> Decorator[D]:
        return Decorator(
            name=func.__name__,
            func=func,
            inherit=inherit,
        )

    return inner


def remove(*decos: Decorator) -> t.Callable[[Command], Command]:
    """Decorator that removes all `*decos` from the decorated `command`"""

    def inner(command: Command) -> Command:
        for dc in decos:
            dc.remove(command)

        return command

    return inner


def error_handler(*errors: type[Exception], inherit: bool = False):
    from arc.context import Context

    def inner(func: D) -> Decorator[t.Callable[[], t.Generator[None, t.Any, None]]]:
        def handle_errors(*args, **kwargs) -> t.Generator[None, t.Any, None]:
            try:
                yield
            except errors as e:
                func(e, Context.current())

        return Decorator(
            name=func.__name__,
            func=handle_errors,
            inherit=inherit,
        )

    return inner
