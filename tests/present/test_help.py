import arc
from arc import utils


def get_lines(string: str, from_line: int, to_line: int):
    return "\n".join(string.split("\n")[from_line:to_line])


def test_basic():
    @arc.command()
    def command():
        ...

    assert (
        utils.ansi_clean(command.doc.help())
        == """\
USAGE
    command [-h]

OPTIONS
    --help (-h)  Displays this help message
"""
    )


def test_description():
    @arc.command()
    def command():
        """Here's a description"""

    assert (
        utils.ansi_clean(command.doc.help())
        == """\
USAGE
    command [-h]

DESCRIPTION
    Here's a description

OPTIONS
    --help (-h)  Displays this help message
"""
    )


def test_advanced_parsing():
    @arc.command()
    def command():
        """Here's a description

        Here's another description paragraph

        # Section
        Here's an additional section

        \b
        - 1
        - 2
        - 3
        """

    assert (
        utils.ansi_clean(command.doc.help())
        == """\
USAGE
    command [-h]

DESCRIPTION
    Here's a description

    Here's another description paragraph

OPTIONS
    --help (-h)  Displays this help message

SECTION
    Here's an additional section

    - 1
    - 2
    - 3
"""
    )


def test_subcommands():
    @arc.command()
    def command():
        ...

    @command.subcommand()
    def sub():
        ...

    @sub.subcommand()
    def sub2():
        ...

    # How the root command should behave
    assert (
        utils.ansi_clean(command.doc.help())
        == """\
USAGE
    command [-h]
    command <subcommand> [ARGUMENTS ...]

OPTIONS
    --help (-h)  Displays this help message

SUBCOMMANDS
    sub
"""
    )

    assert (
        utils.ansi_clean(sub.doc.help())
        == """\
USAGE
    command sub [-h]
    command sub <subcommand> [ARGUMENTS ...]

OPTIONS
    --help (-h)  Displays this help message

SUBCOMMANDS
    sub2
"""
    )

    assert (
        utils.ansi_clean(sub2.doc.help())
        == """\
USAGE
    command sub sub2 [-h]

OPTIONS
    --help (-h)  Displays this help message
"""
    )


def test_namespace():

    ns = arc.namespace("ns", description="ns description")

    @ns.subcommand()
    def command1():
        """command1 desc"""

    @ns.subcommand()
    def command2():
        """command2 desc"""

    assert (
        utils.ansi_clean(ns.doc.help())
        == """\
USAGE
    ns [-h]
    ns <subcommand> [ARGUMENTS ...]

DESCRIPTION
    ns description

OPTIONS
    --help (-h)  Displays this help message

SUBCOMMANDS
    command1     command1 desc
    command2     command2 desc
"""
    )


ARGS_STR = """\
USAGE
    command [-h] [--key-opt KEY-OPT] [--flag] --key-req KEY-REQ [--] pos-req [pos-
    opt]

ARGUMENTS
    pos-req      positional required
    pos-opt      positional optional

OPTIONS
    --help (-h)  Displays this help message
    --key-req    key required
    --key-opt    key optional
    --flag       flag
"""


def test_argument_desc_in_definition():
    @arc.command()
    def command(
        pos_req: int = arc.Argument(description="positional required"),
        pos_opt: int = arc.Argument(description="positional optional", default=1),
        key_req: int = arc.Option(description="key required"),
        key_opt: int = arc.Option(description="key optional", default=1),
        flag: bool = arc.Flag(description="flag"),
    ):
        ...

    assert utils.ansi_clean(command.doc.help()) == ARGS_STR


def test_argument_desc_in_docstring():
    @arc.command()
    def command(
        pos_req: int,
        pos_opt: int = 1,
        *,
        key_req: int,
        key_opt: int = 1,
        flag: bool,
    ):
        """
        # Arguments
        pos_req: positional required
        pos_opt: positional optional
        key_req: key required
        key_opt: key optional
        flag: flag
        """

    assert utils.ansi_clean(command.doc.help()) == ARGS_STR
