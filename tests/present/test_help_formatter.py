import pytest
from arc._command.command import Command
from arc.config import config
from arc import CLI, command
from arc.present.help_formatter import HelpFormatter
from arc.types import Param
from arc.context import Context

# Because pytest is the program that is executing these tests, it will be the automatic name
# for commands that do not specify an explicit name


@pytest.fixture(scope="module", autouse=True)
def disable_ansi():
    config.ansi = False
    yield
    config.ansi = True


def get_lines(string: str, from_line: int, to_line: int):
    return "\n".join(string.split("\n")[from_line:to_line])


def test_command():
    @command()
    def test(val: int = Param(description="Some cool value")):
        """description"""
        print(val)

    # run so it generates it generates the command name
    test("2")
    assert (
        test.get_help(test.create_ctx(test.name))
        == """\
USAGE
    pytest [--help] [--] val

DESCRIPTION
    description

ARGUMENTS
    val  Some cool value

OPTIONS
    --help (-h)  Shows help documentation
"""
    )


def test_cli(cli: CLI):
    cli.version = "0.0.1"
    del cli.params

    @cli.command()
    def command():
        """description content
        second line
        """

    assert (
        cli.get_help(cli.create_ctx(cli.name))
        == """\
USAGE
    test <command> [ARGUMENTS ...]

OPTIONS
    --help (-h)     Shows help documentation
    --version (-v)  Displays the app's current version

SUBCOMMANDS
    debug           debug utilties for an arc application
    command         description content
"""
    )

    assert (
        command.get_help(cli.create_ctx(cli.name).child_context(command))
        == """\
USAGE
    test command [--help]

DESCRIPTION
    description content second line

OPTIONS
    --help (-h)  Shows help documentation
"""
    )


def test_namespace(cli: CLI):
    debug = cli.subcommands["debug"]
    assert (
        debug.get_help(cli.create_ctx(cli.name).child_context(debug))
        == """\
USAGE
    test debug:<subcommand> [ARGUMENTS ...]

DESCRIPTION
    debug utilties for an arc application

OPTIONS
    --help (-h)  Shows help documentation

SUBCOMMANDS
    config       Displays information about the current config of the arc app
    aliases      Displays information aboubt the currently accessible type
                 aliases
    arcfile      Prints the contents of the .arc file in the CWD
    schema       Prints out a dictionary representation of the CLI
"""
    )


def test_docstring_parsing(cli: CLI):
    @cli.command()
    def command(arg1: int = Param(description="overide"), arg2=Param()):
        """This is the description

        This is a second paragraph

        # Arguments
        arg2: this is a argument description

        # Examples
        \b
        > example 1
        > example 2
        """
        ...

    assert (
        command.get_help(cli.create_ctx(cli.name).child_context(command))
        == """\
USAGE
    test command [--help] [--] arg1 arg2

DESCRIPTION
    This is the description

    This is a second paragraph

ARGUMENTS
    arg1  overide
    arg2  this is a argument description

OPTIONS
    --help (-h)  Shows help documentation

EXAMPLES
    > example 1
    > example 2
"""
    )


def test_preserve_paragraph(cli: CLI):
    @cli.command()
    def command():
        """para 1

        para 2
        """

    assert (
        command.get_help(cli.create_ctx(cli.name).child_context(command))
        == """\
USAGE
    test command [--help]

DESCRIPTION
    para 1

    para 2

OPTIONS
    --help (-h)  Shows help documentation
"""
    )


def test_arguments(cli: CLI):
    @cli.command()
    def command(
        pos_req: int = Param(description="positional required"),
        pos_opt: int = Param(description="positional optional", default=1),
        *,
        key_req: int = Param(description="key required", short="r"),
        key_opt: int = Param(description="key optional", default=1),
        flag: bool = Param(
            description="""
                Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                Proin iaculis vel sapien sit amet facilisis.
                Phasellus purus velit, feugiat non posuere id,
                commodo a odio. Sed nibh tellus, fermentum ac gravida quis,
                commodo sed metus. Suspendisse sed dui nec lacus efficitur
                malesuada. Nullam euismod ante a eros consectetur faucibus."""
        ),
    ):
        ...

    # The text wrapping is not 100% consistent, so this isn't
    # 1-to-1 with the actual execution
    assert (
        command.get_help(cli.create_ctx(cli.name).child_context(command))
        == """\
USAGE
    test command [--key-opt <...>] [--help] [--flag] --key-req <...> [--] pos-
    req [pos-opt]

ARGUMENTS
    pos-req  positional required
    pos-opt  positional optional

OPTIONS
    --help (-h)     Shows help documentation
    --flag          Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    Proin iaculis vel sapien sit amet facilisis. Phasellus
                    purus velit, feugiat non posuere id, commodo a odio. Sed
                    nibh tellus, fermentum ac gravida quis, commodo sed metus.
                    Suspendisse sed dui nec lacus efficitur malesuada. Nullam
                    euismod ante a eros consectetur faucibus.
    --key-req (-r)  key required
    --key-opt       key optional
"""
    )


def test_argument_desc_precedence(cli: CLI):
    """arg1 has a description in the metadata, so it should overide
    the description in the docstring
    """

    @cli.command()
    def command(arg1: int = Param(description="overide"), arg2=Param()):
        """desc

        # Arguments
        arg1: does not show
        arg2: does show
        """
        ...

    assert (
        command.get_help(cli.create_ctx(cli.name).child_context(command))
        == """\
USAGE
    test command [--help] [--] arg1 arg2

DESCRIPTION
    desc

ARGUMENTS
    arg1  overide
    arg2  does show

OPTIONS
    --help (-h)  Shows help documentation
"""
    )
