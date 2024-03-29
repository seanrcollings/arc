from collections import UserDict
import arc
from arc.runtime import Context


def test_install():
    @arc.command
    def command(ctx: Context):
        return ctx

    @command.use
    def middleware(ctx):
        ctx["called"] = True

    assert command()["called"]


def test_ctx():
    @arc.command
    def command(ctx: Context):
        return ctx

    @command.use
    def middleware(ctx: Context):
        ctx["test"] = 1

    assert command()["test"] == 1


def test_replace_ctx():
    class FakeContext(UserDict):
        def __init__(self, data=None, *, logger):
            super().__init__(data)
            self.logger = logger

    @arc.command
    def command(ctx: Context):
        return ctx

    @command.use
    def middleware(ctx: Context):
        return FakeContext({"arc.args": {"ctx": {}}}, logger=ctx.logger)

    assert not isinstance(command(), Context)


def test_yield():
    @arc.command
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
    @arc.command
    def command(ctx: Context):
        return 2

    @command.use
    def middleware(ctx: Context):
        res = yield
        assert res == 2

    assert command() == 2


def test_overwrite_result():
    @arc.command
    def command(ctx: Context):
        return 2

    @command.use
    def middleware(ctx: Context):
        yield
        return 1

    assert command() == 1
