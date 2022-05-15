from __future__ import annotations
import typing as t

from arc import callback as acb

if t.TYPE_CHECKING:
    from arc.context import Context

ErrorHandlerFunc = t.Callable[[Exception, "Context"], t.Optional[bool]]


def create_handler(*exceptions: type[Exception], inherit: bool = True):
    from arc.context import Context

    def inner(callback: ErrorHandlerFunc) -> acb.Callback:
        def callback_wrapper(_args, _ctx):
            try:
                yield
            except exceptions as e:
                callback(e, Context.current())

        cb = acb.create(inherit=inherit)(callback_wrapper)
        return cb

    return inner
