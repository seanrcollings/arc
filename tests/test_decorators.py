import pytest
from arc import Context, errors, decorator
import arc


class CallbackException(Exception):
    """Used to assert that decorators are actually running"""

    def __init__(self, ctx: Context, **kwargs):
        self.ctx = ctx
        self.kwargs = kwargs


def test_execute():
    @decorator()
    def cb(ctx):
        raise CallbackException(ctx)

    @cb
    @arc.command()
    def test():
        return 10

    with pytest.raises(CallbackException):
        test("")

    cb.remove(test)
    assert test("") == 10


def test_exception():
    @decorator()
    def cb(ctx):
        try:
            yield
        except errors.ExecutionError:
            raise CallbackException(ctx)

    @cb
    @arc.command()
    def test():
        raise errors.ExecutionError()

    with pytest.raises(CallbackException):
        test("")


def test_final():
    @decorator()
    def cb(ctx):
        try:
            yield
        finally:
            raise CallbackException(ctx)

    @cb
    @arc.command()
    def test1():
        raise errors.ExecutionError()

    @cb
    @arc.command()
    def test2():
        ...

    with pytest.raises(CallbackException):
        test1("")

    with pytest.raises(CallbackException):
        test2("")


def test_missing_yield():
    """A pure function should still execute"""

    @decorator()
    def cb(ctx):
        raise CallbackException(ctx)

    @cb
    @arc.command()
    def command():
        ...

    with pytest.raises(CallbackException):
        command("")


def test_deco_inheritance():
    @arc.decorator()
    def cb1(args, ctx):
        ...

    @cb1
    @arc.command()
    def command():
        ...

    @command.subcommand()
    def sub():
        ...

    assert cb1 in sub.decorators


def test_decorator_order():
    @arc.decorator()
    def cb1(ctx):
        ctx.state["cb_order"].append("cb1")
        yield
        ctx.state["cb_order"].append("cb1")

    @arc.decorator()
    def cb2(ctx):
        ctx.state["cb_order"].append("cb2")
        yield
        ctx.state["cb_order"].append("cb2")

    @cb1
    @cb2
    @arc.command()
    def command(ctx: Context):
        return ctx.state

    assert command("", state={"cb_order": []}) == {
        "cb_order": ["cb1", "cb2", "cb2", "cb1"]
    }


def test_remove_decorator():
    @arc.decorator()
    def cb(ctx):
        raise CallbackException(ctx)

    @cb
    @arc.command()
    def c1():
        ...

    @c1.subcommand()
    def sub1():
        ...

    @cb.remove
    @c1.subcommand()
    def c2():
        ...

    @c2.subcommand()
    def sub2():
        ...

    with pytest.raises(CallbackException):
        c1("")

    with pytest.raises(CallbackException):
        c1("sub1")

    # Shouldn't raise, because the decorator isn't present
    c1("c2")
    c1("c2 sub2")


def test_non_inheritable():
    @arc.decorator(inherit=False)
    def cb(ctx):
        raise CallbackException(ctx)

    @cb
    @arc.command()
    def command():
        ...

    @command.subcommand()
    def sub():
        ...

    with pytest.raises(CallbackException):
        command("")

    command("sub")
