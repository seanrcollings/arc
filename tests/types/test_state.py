import pytest

import arc
from arc import App, errors, namespace
from arc.runtime import Context
from arc.types import State


@pytest.fixture(scope="function")
def cli():
    cli = arc.namespace("cli")

    @cli.use
    def inject_state(ctx: Context):
        ctx.state["test"] = 1

    return cli


def test_parent_state(cli: arc.Command):
    @cli.subcommand
    def parent_state(val: int, state: State):
        return val, state

    @cli.subcommand
    def ignore_parent_state(val: int):
        return val

    val, state = cli("parent-state 2")
    assert val == 2
    assert state.test == 1
    assert cli("ignore-parent-state 2") == 2


def test_custom_state(cli: arc.Command):
    class CustomState(State):
        ...

    @cli.subcommand
    def custom(state: CustomState):
        return state

    state = cli("custom")
    assert isinstance(state, CustomState)
    assert state.test == 1


def test_override(cli: arc.Command):
    @cli.subcommand
    def override(*, state: State):
        ...

    with pytest.raises(errors.UnrecognizedArgError):
        cli("override --state 2")


def test_state_retained(cli: arc.Command):
    @cli.subcommand
    def c1(ctx: Context, state: State):
        state.val = 2
        return ctx.execute(c2)

    @cli.subcommand
    def c2(state: State):
        return state

    assert cli("c1").val == 2
