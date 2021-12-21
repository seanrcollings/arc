from typing_extensions import TypedDict, get_args
import pytest
from arc import CLI, namespace, errors
from arc.types import State


@pytest.fixture(scope="function")
def scli(cli: CLI):
    cli.state = {"test": 1}
    return cli


def test_parent_state(scli: CLI):
    @scli.subcommand()
    def parent_state(val: int, state: State):
        return val, state

    @scli.subcommand()
    def ignore_parent_state(val: int):
        return val

    val, state = scli("parent-state 2")
    assert val == 2
    assert state.test == 1
    assert scli("ignore-parent-state 2") == 2


def test_my_state(scli: CLI):
    @scli.subcommand(state={"test2": 3})
    def local_state(state: State):
        return state

    state = scli("local-state")
    assert state.test == 1
    assert state.test2 == 3


def test_state_name(scli: CLI):
    @scli.subcommand()
    def other_state_name(foo: State):
        return foo

    state = scli("other-state-name")
    assert state.test == 1


def test_propagate(scli: CLI):
    ns = namespace("ns")

    @ns.subcommand(state={"test2": 2})
    def test(state: State):
        return state

    scli.install_command(ns)
    state = scli("ns:test")
    assert state.test == 1
    assert state.test2 == 2


def test_custom_state(scli: CLI):
    class CustomState(State):
        ...

    @scli.subcommand()
    def custom(state: CustomState):
        return state

    state = scli("custom")
    assert isinstance(state, CustomState)
    assert state.test == 1


def test_override(scli: CLI):
    @scli.subcommand()
    def override(state: State):
        ...

    with pytest.raises(errors.UnrecognizedArgError):
        scli("override --state 2")
