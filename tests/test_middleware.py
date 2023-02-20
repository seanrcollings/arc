import pytest
import arc
from arc.context import Context


def test_install():
    @arc.command()
    def command(ctx: Context):
        return ctx

    @command.use
    def middleware(ctx):
        ctx["called"] = True

    assert command()["called"]


def test_ctx():
    @arc.command()
    def command(ctx: Context):
        return ctx

    @command.use
    def middleware(ctx: Context):
        ctx["test"] = 1

    assert command()["test"] == 1


def test_replace_ctx():
    @arc.command()
    def command(ctx: Context):
        return ctx

    @command.use
    def middleware(ctx: Context):
        return {"arc.args": {"ctx": {}}}

    assert not isinstance(command(), Context)


def test_yield():
    @arc.command()
    def command(ctx: Context):
        return ctx

    @command.use
    def middleware(ctx: Context):
        ctx["before"] = True
        yield
        ctx["after"] = True

    ctx = command()

    assert ctx["before"]
    assert ctx["after"]


def test_yield_results():
    @arc.command()
    def command(ctx: Context):
        return 2

    @command.use
    def middleware(ctx: Context):
        res = yield
        assert res == 2

    assert command() == 2


def test_overwrite_result():
    @arc.command()
    def command(ctx: Context):
        return 2

    @command.use
    def middleware(ctx: Context):
        yield
        return 1

    assert command() == 1
