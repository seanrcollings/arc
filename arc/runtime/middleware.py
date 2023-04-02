from __future__ import annotations

import abc
import collections
import types
import typing as t

import arc
from arc import errors

if t.TYPE_CHECKING:
    from arc.runtime import Context


MiddlewareGenerator = t.Generator["Context", t.Any, t.Any]
Middleware = t.Callable[["Context"], t.Union["Context", MiddlewareGenerator, None]]
ErrorHandler = t.Callable[["Context", BaseException], t.Any]


class MiddlewareBase(abc.ABC):
    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    @abc.abstractmethod
    def __call__(self, ctx: Context) -> t.Any:
        ...


class MiddlewareStack(collections.UserList[Middleware]):
    __gens: list[t.Generator[None, t.Any, None]]

    def __repr__(self) -> str:
        return f"MiddlewareStack({self.data!r})"

    def start(self, ctx: Context) -> Context:
        self.__gens = []

        for handler in self:
            res = handler(ctx)
            if isinstance(res, types.GeneratorType):
                self.__gens.append(res)
                res = next(res)

            res = t.cast(t.Union["Context", None], res)

            if res is not None:
                ctx = res

        return ctx

    def close(self, result: t.Any) -> t.Any:
        """Closes each callback by calling `next()` on them"""
        for gen in reversed(self.__gens):
            try:
                gen.send(result)
            except StopIteration as e:
                if e.value is not None:
                    result = e.value

        return result

    def throw(self, exception: Exception) -> None:
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

    def try_remove(self, m: Middleware) -> None:
        try:
            self.remove(m)
        except ValueError:
            ...


class MiddlewareContainer:
    def __init__(self, middlewares: t.Sequence[Middleware]):
        self.stack = MiddlewareStack(middlewares)

    @t.overload
    def use(
        self,
        handler: None = None,
        *,
        pos: int | None = None,
        replace: Middleware | None = None,
        before: Middleware | None = None,
        after: Middleware | None = None,
    ) -> t.Callable[[Middleware], Middleware]:
        ...

    @t.overload
    def use(
        self,
        handler: Middleware,
        *,
        pos: int | None = None,
        replace: Middleware | None = None,
        before: Middleware | None = None,
        after: Middleware | None = None,
    ) -> Middleware:
        ...

    @t.overload
    def use(
        self,
        handler: t.Sequence[Middleware],
        *,
        pos: int | None = None,
        replace: Middleware | None = None,
        before: Middleware | None = None,
        after: Middleware | None = None,
    ) -> t.Sequence[Middleware]:
        ...

    def use(
        self,
        handler: t.Any = None,
        *,
        pos: int | None = None,
        replace: Middleware | None = None,
        before: Middleware | None = None,
        after: Middleware | None = None,
    ) -> t.Any:
        """Register a middleware with this object.

        Args:
            handler (callable, optional): Callable to register as a middleware.
                Can optionally receive an array of middlewares.
            pos (int | None, optional): Index in the middleware stack to insert this middleware. Defaults to None.
            replace (Middleware | None, optional): A middleware you want to replace with this middleware. Defaults to None.
            before (Middleware | None, optional): Insert the provided `handler` before this middleware. Defaults to None.
            after (Middleware | None, optional): Insert the provided `handler` after this middleware. Defaults to None.
        """

        def ensure_single_operation() -> None:
            ops = [op for op in (pos, replace, before, after) if op is not None]
            if len(ops) > 1:
                raise errors.InternalError(
                    "Cannot provide multiple operations for a single middleware"
                )

        def inner(handler: Middleware) -> Middleware:
            ensure_single_operation()
            if pos is not None:
                self.stack.insert(pos, handler)
            elif replace:
                idx = self.stack.index(replace)
                self.stack[idx] = handler
            elif before:
                idx = self.stack.index(before)
                self.stack.insert(idx - 1, handler)
            elif after:
                idx = self.stack.index(after)
                self.stack.insert(idx + 1, handler)
            else:
                self.stack.append(handler)

            return handler

        if handler:
            if callable(handler):
                return inner(handler)
            else:
                return [inner(f) for f in handler]

        return inner

    @t.overload
    def handle(  # type: ignore
        self, *exceptions: type[BaseException]
    ) -> t.Callable[[ErrorHandler], ErrorHandler]:
        ...

    @t.overload
    def handle(
        self, handler: ErrorHandler, *exceptions: type[BaseException]
    ) -> ErrorHandler:
        ...

    @t.overload
    def handle(
        self, handler: t.Sequence[ErrorHandler], *exceptions: type[BaseException]
    ) -> list[ErrorHandler]:
        ...

    def handle(self, handler: t.Any | type = None, *exceptions: t.Any) -> t.Any:
        """Register an exception handler to this object

        Args:
            handler (ErrorHandler, optional): Error handler callback, receives the context
                and the exception object.
        """

        def inner(func: ErrorHandler) -> ErrorHandler:
            @self.use
            def error_handler(ctx: Context) -> t.Any:
                try:
                    yield
                except exceptions as e:
                    return func(ctx, e)

            return func

        if issubclass(handler, BaseException):
            exceptions = (handler, *exceptions)
            return inner
        elif callable(handler):
            return inner(handler)
        else:
            return [inner(f) for f in handler]


class DefaultMiddlewareNamespace:
    _list: list[Middleware]

    @classmethod
    def all(cls) -> list[Middleware]:
        """Returns a list of all default middlewares"""
        return cls._list

    @classmethod
    def regsiter(cls, name: str, middleware: Middleware) -> None:
        """Register a new default middleware."""
        cls._list.append(middleware)
        setattr(cls, name, middleware)
