# import pytest
# from arc import CLI, namespace, errors
# from arc.context import Context
# from arc.types import State


# @pytest.fixture(scope="function")
# def scli():
#     cli.state = {"test": 1}
#     return cli


# def test_parent_state():
#     @scli.subcommand()
#     def parent_state(val: int, state: State):
#         return val, state

#     @scli.subcommand()
#     def ignore_parent_state(val: int):
#         return val

#     val, state = scli("parent-state 2")
#     assert val == 2
#     assert state.test == 1
#     assert scli("ignore-parent-state 2") == 2


# def test_my_state():
#     @scli.subcommand(state={"test2": 3})
#     def local_state(state: State):
#         return state

#     state = scli("local-state")
#     assert state.test == 1
#     assert state.test2 == 3


# def test_state_name():
#     @scli.subcommand()
#     def other_state_name(foo: State):
#         return foo

#     state = scli("other-state-name")
#     assert state.test == 1


# def test_propagate():
#     ns = namespace("ns")

#     @ns.subcommand(state={"test2": 2})
#     def test(state: State):
#         return state

#     scli.install_command(ns)
#     state = scli("ns:test")
#     assert state.test == 1
#     assert state.test2 == 2


# def test_custom_state():
#     class CustomState(State):
#         ...

#     @scli.subcommand()
#     def custom(state: CustomState):
#         return state

#     state = scli("custom")
#     assert isinstance(state, CustomState)
#     assert state.test == 1


# def test_override():
#     @scli.subcommand()
#     def override(state: State):
#         ...

#     with pytest.raises(errors.UnrecognizedArgError):
#         scli("override --state 2")


# def test_state_retained():
#     @scli.subcommand()
#     def c1(ctx: Context, state: State):
#         state.val = 2
#         return ctx.execute(c2)

#     @scli.subcommand()
#     def c2(state: State):
#         return state

#     assert scli("c1").val == 2


# def test_state_persitance():
#     class CustomState(State):
#         ...

#     @scli.options
#     def options(state: CustomState):
#         state.o_val = 1

#     @scli.callback()
#     def callback(_args, ctx):
#         ctx.state.ca_val = 1
#         yield

#     @scli.subcommand()
#     def c1(state: CustomState):
#         state.co_val = 1
#         return state

#     assert scli("c1") == CustomState(o_val=1, ca_val=1, co_val=1, test=1)
