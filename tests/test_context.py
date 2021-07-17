import pytest
from arc import run, CLI, namespace, errors
from arc.command import Context


@pytest.fixture
def ctx_cli(cli: CLI):
    cli.context = {"test": 1}
    return cli


def test_parent_context(ctx_cli: CLI):
    @ctx_cli.subcommand()
    def parent_context(val: int, context: Context):
        return val, context

    @ctx_cli.subcommand()
    def ignore_parent_context(val: int):
        return val

    assert ctx_cli("parent-context val=2") == (2, Context({"test": 1}))
    assert ctx_cli("ignore-parent-context val=2") == 2


def test_my_context(ctx_cli: CLI):
    @ctx_cli.subcommand(context={"test2": 3})
    def local_context(context: Context):
        return context

    assert ctx_cli("local-context") == Context({"test": 1, "test2": 3})


def test_context_name(ctx_cli: CLI):
    @ctx_cli.subcommand()
    def other_context_name(foo: Context):
        return foo

    assert ctx_cli("other-context-name") == Context({"test": 1})


def test_propagate(ctx_cli: CLI):
    ns = namespace("ns")

    @ns.subcommand(context={"test2": 2})
    def test(ctx: Context):
        return ctx

    ctx_cli.install_command(ns)
    assert ctx_cli("ns:test") == Context({"test": 1, "test2": 2})


def test_custom_context(ctx_cli: CLI):
    class CustomContext(Context):
        ...

    @ctx_cli.subcommand()
    def custom(ctx: CustomContext):
        return ctx

    assert ctx_cli("custom") == CustomContext({"test": 1})


def test_override(ctx_cli: CLI):
    @ctx_cli.subcommand()
    def override(ctx: Context):
        ...

    with pytest.raises(errors.MissingArgError):
        ctx_cli("override --ctx 2")
