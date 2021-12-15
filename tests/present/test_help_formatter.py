# import pytest
# from arc.command.command import Command
# from arc.execution_state import ExecutionState
# from arc.config import config
# from arc import CLI
# from arc.present.help_formatter import HelpFormatter
# from arc.types import Param


# @pytest.fixture(scope="module", autouse=True)
# def disable_ansi():
#     config.ansi = False
#     yield
#     config.ansi = True


# def gen_help(command: Command, state: ExecutionState = None, **kwargs):
#     f = HelpFormatter(**kwargs)
#     f.write_help(command, state)
#     return f


# def gen_state(parent: Command, *commands: Command):
#     state = ExecutionState.empty()
#     state.command_chain = [parent, *commands]
#     state.command_namespace = [command.name for command in commands]
#     return state


# def get_lines(string: str, from_line: int, to_line: int):
#     return "\n".join(string.split("\n")[from_line:to_line])


# def test_basic(cli: CLI):
#     @cli.command()
#     def test():
#         """description content
#         second line
#         """

#     f = gen_help(cli, width=80)
#     assert (
#         f.value
#         == """\
# USAGE
#     cli <command> [arguments ...]

# DESCRIPTION
#     View specific help with "help <command-name>"

# ARGUMENTS
#     --help (-h)     display this help
#     --version (-v)  display application version

# SUBCOMMANDS
#     debug           debug utilties for an arc application
#     help            Displays information for a given command
#     test            description content
# """
#     )

#     state = gen_state(cli, test)
#     f = gen_help(test, state, width=80)
#     assert (
#         f.value
#         == """\
# USAGE
#     cli test

# DESCRIPTION
#     description content second line
# """
#     )


# def test_docstring_parsing(cli: CLI):
#     @cli.command()
#     def test(arg1: int = Param(description="overide"), arg2=Param()):
#         """This is the descriptions

#         This is a second paragraph

#         # Arguments
#         arg2: this is a argument description

#         # Examples
#         \b
#         > example 1
#         > example 2
#         """
#         ...

#     state = gen_state(cli, test)
#     f = gen_help(test, state, width=80)
#     assert (
#         f.value
#         == """\
# USAGE
#     cli test <arg1> <arg2>

# DESCRIPTION
#     This is the descriptions

#     This is a second paragraph

# ARGUMENTS
#     <arg1>  overide
#     <arg2>  this is a argument description

# EXAMPLES
#     > example 1
#     > example 2
# """
#     )


# def test_preserve_paragraph(cli: CLI):
#     @cli.command()
#     def test():
#         """para 1

#         para 2
#         """

#     state = gen_state(cli, test)
#     f = gen_help(test, state, width=80)
#     assert (
#         f.value
#         == """\
# USAGE
#     cli test

# DESCRIPTION
#     para 1

#     para 2
# """
#     )


# def test_arguments(cli: CLI):
#     @cli.command()
#     def command(
#         pos_req: int = Param(description="positional required"),
#         pos_opt: int = Param(description="positional optional", default=1),
#         *,
#         key_req: int = Param(description="key required", short="r"),
#         key_opt: int = Param(description="key required", default=1),
#         flag: bool = Param(
#             description="""
#                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#                 Proin iaculis vel sapien sit amet facilisis.
#                 Phasellus purus velit, feugiat non posuere id,
#                 commodo a odio. Sed nibh tellus, fermentum ac gravida quis,
#                 commodo sed metus. Suspendisse sed dui nec lacus efficitur
#                 malesuada. Nullam euismod ante a eros consectetur faucibus."""
#         ),
#     ):
#         ...

#     state = gen_state(cli, command)
#     f = gen_help(command, state, width=100)

#     assert (
#         f.value
#         == """\
# USAGE
#     cli command --key-req <...> [--key-opt <...>] [--flag] [--] <pos-req> [pos-opt]

# ARGUMENTS
#     <pos-req>       positional required
#     <pos-opt>       positional optional
#     --key-req (-r)  key required
#     --key-opt       key required
#     --flag          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin iaculis vel
#                     sapien sit amet facilisis. Phasellus purus velit, feugiat non posuere id,
#                     commodo a odio. Sed nibh tellus, fermentum ac gravida quis, commodo sed metus.
#                     Suspendisse sed dui nec lacus efficitur malesuada. Nullam euismod ante a eros
#                     consectetur faucibus.
# """
#     )


# def test_argument_desc_precedence(cli: CLI):
#     """arg1 has a description in the metadata, so it should overide
#     the description in the docstring
#     """

#     @cli.command()
#     def test(arg1: int = Param(description="overide"), arg2=Param()):
#         """desc

#         # Arguments
#         arg1: does not show
#         arg2: does show
#         """
#         ...

#     state = gen_state(cli, test)
#     f = gen_help(test, state, width=100)
#     assert (
#         f.value
#         == """\
# USAGE
#     cli test <arg1> <arg2>

# DESCRIPTION
#     desc

# ARGUMENTS
#     <arg1>  overide
#     <arg2>  does show
# """
#     )
