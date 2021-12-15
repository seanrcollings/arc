# from typing import Annotated
# import pytest
# from arc import CLI, errors
# from arc.types import VarPositional, VarKeyword, Param, PosParam, KeyParam, FlagParam


# def test_basic(cli: CLI):
#     @cli.subcommand()
#     class Test:
#         val: int

#         def handle(self):
#             return self.val

#     assert cli("Test 2") == 2

#     with pytest.raises(errors.ArgumentError):
#         cli("Test")


# def test_default(cli: CLI):
#     @cli.subcommand()
#     class Test:
#         val: int = 2

#         def handle(self):
#             return self.val

#     assert cli("Test") == 2
#     assert cli("Test --val 3") == 3


# def test_short_args(cli: CLI):
#     @cli.subcommand()
#     class Test:
#         val: int = KeyParam(short="v")

#         def handle(self):
#             return self.val

#     assert cli("Test --val 3") == 3
#     assert cli("Test -v 3") == 3


# def test_no_handle(cli: CLI):
#     with pytest.raises(errors.CommandError):

#         @cli.subcommand()
#         class Test:
#             ...


# def test_var_pos(cli: CLI):
#     @cli.subcommand()
#     class Test:
#         arg1: int
#         args: VarPositional[int]

#         def handle(self):
#             return self.args

#     assert cli("Test 11 11 11") == [11, 11]


# def test_var_keyword(cli: CLI):
#     @cli.subcommand()
#     class Test:
#         args: VarKeyword[int]

#         def handle(self):
#             return self.args

#     assert cli("Test --val1 11 --val2 11 --val3 11") == {
#         "val1": 11,
#         "val2": 11,
#         "val3": 11,
#     }
