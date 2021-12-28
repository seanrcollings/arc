import pytest
from arc import CLI, Context, errors, callback


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


def test_inheritance(cli: CLI):
    @callback.create()
    def cb(_args, ctx):
        raise CallbackException(ctx)

    @callback.create(inherit=False)
    def cb2(_args, ctx):
        raise CallbackException(ctx)

    @cb
    @cb2
    @cli.subcommand()
    def command():
        ...

    @command.subcommand()
    def sub1():
        ...

    assert cb in sub1.callbacks
    assert cb2 not in sub1.callbacks
    with pytest.raises(CallbackException):
        cli("command:sub1")

    @callback.remove(cb)
    @command.subcommand()
    def sub2():
        ...

    assert cb not in sub2.callbacks
    cli("command:sub2")

    @cb.remove
    @command.subcommand()
    def sub3():
        ...

    assert cb not in sub3.callbacks
    cli("command:sub3")


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
