# import pytest

# from arc import callbacks, errors, CLI
# from arc.result import Ok, Err


# @callbacks.before
# def before(args):
#     ...


# def test_exec_time(cli: CLI):
#     @callbacks.before
#     def raise_before(_):
#         raise errors.ValidationError()

#     @callbacks.after
#     def raise_after(_):
#         raise errors.ValidationError()

#     @raise_before
#     @cli.subcommand()
#     def top():
#         assert False, "Command Should not execute"

#     with pytest.raises(errors.ValidationError):
#         cli("top")

#     @raise_after
#     @cli.subcommand()
#     def bottom():
#         assert True, "Command Should Execute"

#     with pytest.raises(errors.ValidationError):
#         cli("bottom")


# def test_around(cli: CLI):
#     @callbacks.around
#     def before(arguments):
#         assert arguments == {"val": 2}
#         val = yield
#         assert val == Ok(4)

#     @before
#     @cli.subcommand()
#     def thing(val: int):
#         return val + 2

#     assert cli("thing 2") == 4


# def test_inheritance(cli: CLI):
#     @callbacks.before(inherit=False)
#     def no_inherit(args):
#         ...

#     @no_inherit
#     @before
#     @cli.subcommand()
#     def top():
#         ...

#     @top.subcommand()
#     def thing():
#         ...

#     assert no_inherit.__wrapped__ not in thing.executable.callback_store["before"]  # type: ignore
#     assert before.__wrapped__ in thing.executable.callback_store["before"]  # type: ignore


# def test_skip(cli: CLI):
#     @before
#     @cli.subcommand()
#     def top():
#         ...

#     @callbacks.skip(before)
#     @top.subcommand()
#     def sub():
#         ...

#     assert before.__wrapped__ in top.executable.callback_store["before"]  # type: ignore
#     assert before.__wrapped__ not in sub.executable.callback_store["before"]  # type: ignore


# def test_callback_args(cli: CLI):
#     @callbacks.before
#     def with_args(arg1, arg2):
#         assert (arg1, arg2) == ("arg1", "arg2")

#         def inner(arguments):
#             assert arguments == {"val": 2}

#         return inner

#     @with_args("arg1", "arg2")
#     @cli.subcommand()
#     def func(val: int):
#         return val

#     assert cli("func 2") == 2