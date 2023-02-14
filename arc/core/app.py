from __future__ import annotations
import types
import typing as t

import arc
import arc.typing as at


if t.TYPE_CHECKING:
    from arc.core import Command
    from arc.context import Context


MiddlewareGenerator = t.Generator["Context", t.Any, t.Any]
Middleware = t.Callable[["Context"], t.Union["Context", MiddlewareGenerator, None]]


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

    def add(self, deco: Middleware):
        self.__middlewares.append(deco)

    def remove(self, deco: Middleware):
        self.__middlewares.remove(deco)

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
                if isinstance(e, arc.errors.Exit):
                    raise e

                exception = e

        if not exception_handled:
            raise exception


class MiddlewareContainer:
    def __init__(self, middlewares: t.Sequence[Middleware]):
        self._stack = MiddlewareStack(middlewares)

    @t.overload
    def use(self, callable: None) -> t.Callable[[Middleware], Middleware]:
        ...

    @t.overload
    def use(self, callable: Middleware) -> Middleware:
        ...

    def use(self, callable: Middleware = None):
        def inner(func: Middleware):
            self._stack.add(func)
            return func

        if callable:
            return inner(callable)

        return inner


class App(MiddlewareContainer):
    def __init__(
        self,
        root,
        config,
        init_middlewares=None,
        state=None,
        ctx=None,
    ) -> None:
        super().__init__(init_middlewares or [])
        self.root = root
        self.config = config
        self.provided_ctx = ctx or {}
        self.state = state or {}

    def __call__(self, input=None) -> t.Any:
        ctx = self.create_ctx({"arc.input": input})
        ctx = self._stack.start(ctx)
        command: Command = ctx["arc.command"]
        res = command.run(ctx)
        res = self._stack.close(res)
        return res

    def create_ctx(self, data: dict = None) -> arc.Context:
        return arc.Context(
            {
                "arc.root": self.root,
                "arc.config": self.config,
                "arc.errors": [],
                "arc.app": self,
                "arc.state": self.state,
            }
            | self.provided_ctx
            | (data or {})
        )
