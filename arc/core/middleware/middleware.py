from __future__ import annotations
import types
import typing as t
import arc

if t.TYPE_CHECKING:
    from arc.context import Context


MiddlewareGenerator = t.Generator["Context", t.Any, t.Any]
Middleware = t.Callable[["Context"], t.Union["Context", MiddlewareGenerator, None]]


class MiddlewareBase:
    def __init__(self) -> None:
        self.app = lambda ctx: None

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.app!r})"

    def __call__(self, ctx: Context) -> t.Any:
        return self.app(ctx)


class MiddlewareStack:
    __middlewares: list[Middleware]
    __gens: list[t.Generator[None, t.Any, None]]

    def __repr__(self):
        return f"MiddlewareStack({self.__middlewares!r})"

    def __init__(self, middlewares: t.Sequence[Middleware] = None):
        self.__middlewares = list(middlewares or [])

    def __iter__(self):
        yield from self.__middlewares

    def __contains__(self, value):
        return value in self.__decos

    def start(self, ctx):
        self.__gens = []

        for middleware in self.__middlewares:
            res = middleware(ctx)
            if isinstance(res, types.GeneratorType):
                self.__gens.append(res)
                res = next(res)

            if res is not None:
                ctx = res

        return ctx

    def close(self, result: t.Any):
        """Closes each callback by calling `next()` on them"""
        for gen in reversed(self.__gens):
            try:
                gen.send(result)
            except StopIteration as e:
                if e.value is not None:
                    result = e.value

        return result

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
                exception = e

        if not exception_handled:
            raise exception

    def add(self, middleware: Middleware):
        self.__middlewares.append(middleware)

    def remove(self, middleware: Middleware):
        self.__middlewares.remove(middleware)

    def clear(self) -> list[Middleware]:
        ret = self.__middlewares
        self.__middlewares = []
        return ret


class MiddlewareContainer:
    def __init__(self, middlewares: t.Sequence[Middleware]):
        self.stack = MiddlewareStack(middlewares)

    @t.overload
    def use(self, func: None) -> t.Callable[[Middleware], Middleware]:
        ...

    @t.overload
    def use(self, func: Middleware) -> Middleware:
        ...

    @t.overload
    def use(self, func: t.Sequence[Middleware]) -> t.Sequence[Middleware]:
        ...

    def use(self, func):
        def inner(func: Middleware):
            self.stack.add(func)
            return func

        if func:
            if callable(func):
                return inner(func)
            else:
                return [inner(f) for f in func]

        return inner
