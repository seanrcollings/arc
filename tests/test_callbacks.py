import pytest
from arc import CLI, Context, errors, callback
import arc


class CallbackException(Exception):
    """Used to assert that callbacks are actually running"""

    def __init__(self, ctx: Context, **kwargs):
        self.ctx = ctx
        self.kwargs = kwargs


def test_execute(cli: CLI):
    @callback.create()
    def cb(_args, ctx):
        raise CallbackException(ctx)

    @cb
    @cli.command()
    def test():
        return 10

    with pytest.raises(CallbackException):
        cli("test")

    cb.remove(test)
    assert cli("test") == 10


def test_exception(cli: CLI):
    @callback.create()
    def cb(_args, ctx):
        try:
            yield
        except errors.ExecutionError:
            raise CallbackException(ctx)

    @cb
    @cli.command()
    def test():
        raise errors.ExecutionError()

    with pytest.raises(CallbackException):
        cli("test")


def test_final(cli: CLI):
    @callback.create()
    def cb(_args, ctx):
        try:
            yield
        finally:
            raise CallbackException(ctx)

    @cb
    @cli.command()
    def test1():
        raise errors.ExecutionError()

    @cb
    @cli.command()
    def test2():
        ...

    with pytest.raises(CallbackException):
        cli("test1")

    with pytest.raises(CallbackException):
        cli("test2")


def test_missing_yield(cli: CLI):
    @callback.create()
    def cb(_args, ctx):
        ...

    @cb
    @cli.subcommand()
    def command():
        ...

    with pytest.raises(errors.CallbackError):
        cli("command")


def test_callback_alias(cli: CLI):
    @cli.callback()
    def cb(_args, ctx):
        raise CallbackException(ctx)

    @cli.command()
    def command():
        ...

    with pytest.raises(CallbackException):
        cli("command")


def test_no_callback_with_options(cli: CLI):
    @cli.callback()
    def callback(_args, ctx: Context):
        ctx.state.setdefault("call_count", 0)
        ctx.state.call_count += 1
        yield

    @cli.command()
    def command(ctx: Context):
        return ctx

    assert cli("command").state.call_count == 1


def test_post_creation_registration(cli: CLI):
    @cli.command()
    def command():
        ...

    @cli.callback()
    def callback(_args, ctx: Context):
        raise CallbackException(ctx)

    with pytest.raises(CallbackException):
        cli("command")


def test_preserve_callbacks(cli: CLI):
    @arc.command()
    def command():
        ...

    @command.callback()
    def cb1(args, ctx):
        ...

    cli.install_command(command)
    assert cb1 in command.callbacks


def test_callback_order(cli: CLI):
    cli.state = {"cb_order": []}

    @cli.callback()
    def cb1(_args, ctx):
        ctx.state["cb_order"].append("cb1")
        yield

    @cli.callback()
    def cb2(args, ctx):
        ctx.state["cb_order"].append("cb2")
        yield

    @cli.command()
    def command(ctx: Context):
        return ctx.state

    assert cli("command") == {"cb_order": ["cb1", "cb2"]}


def test_single_command():
    @arc.command()
    def command():
        ...

    @command.callback()
    def cb(args, ctx):
        raise CallbackException(ctx)

    with pytest.raises(CallbackException):
        command("")


def test_remove_callback(cli: CLI):
    @cli.callback()
    def cb(args, ctx):
        raise CallbackException(ctx)

    @cli.command()
    def c1():
        ...

    @c1.subcommand()
    def sub1():
        ...

    @cb.remove
    @cli.command()
    def c2():
        ...

    @c2.subcommand()
    def sub2():
        ...

    with pytest.raises(CallbackException):
        cli("c1")

    with pytest.raises(CallbackException):
        cli("c1:sub1")

    cli("c2")
    cli("c2:sub2")
