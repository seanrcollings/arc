import arc
from arc.present import Ansi


def test_basic():
    @arc.command
    def command():
        ...

    assert (
        Ansi.clean(command.doc.help())
        == """\
USAGE
    command [-h]

OPTIONS
    --help (-h)  Displays this help message
"""
    )


def test_description():
    @arc.command
    def command():
        """Here's a description"""

    assert (
        Ansi.clean(command.doc.help())
        == """\
USAGE
    command [-h]

DESCRIPTION
    Here's a description

OPTIONS
    --help (-h)  Displays this help message
"""
    )


def test_subcommands():
    @arc.command
    def command():
        ...

    @command.subcommand
    def sub():
        ...

    @sub.subcommand
    def sub2():
        ...

    # How the root command should behave
    assert (
        Ansi.clean(command.doc.help())
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
        Ansi.clean(sub.doc.help())
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
        Ansi.clean(sub2.doc.help())
        == """\
USAGE
    command sub sub2 [-h]

OPTIONS
    --help (-h)  Displays this help message
"""
    )


def test_namespace():

    ns = arc.namespace("ns", desc="ns description")

    @ns.subcommand
    def command1():
        """command1 desc"""

    @ns.subcommand
    def command2():
        """command2 desc"""

    assert (
        Ansi.clean(ns.doc.help())
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
    command [-h] [--key-opt KEY-OPT] [--flag] --key-req KEY-REQ pos-req [pos-
    opt]

ARGUMENTS
    pos-req      positional required
    pos-opt      positional optional (default: 1)

OPTIONS
    --help (-h)  Displays this help message
    --key-req    key required
    --key-opt    key optional (default: 1)
    --flag       flag
"""


def test_argument_desc_in_definition():
    @arc.command
    def command(
        pos_req: int = arc.Argument(desc="positional required"),
        pos_opt: int = arc.Argument(desc="positional optional", default=1),
        key_req: int = arc.Option(desc="key required"),
        key_opt: int = arc.Option(desc="key optional", default=1),
        flag: bool = arc.Flag(desc="flag"),
    ):
        ...

    assert Ansi.clean(command.doc.help()) == ARGS_STR


def test_collections():
    @arc.command
    def command(
        val: list[int],
        val2: tuple[int, int],
        val3: list[int] = [],
        val4: tuple[int, int] = (1, 2),
    ):
        assert Ansi.clean(command.doc.help) == (
            """\
USAGE
    cli.py [-h] val [val...] val2 val2 [val3 [val3...]] [val4] [val4]

ARGUMENTS
    val
    val2
    val3
    val4

OPTIONS
    --help (-h)  Displays this help message
"""
        )


def test_default():
    @arc.command
    def command(val: int = 1):
        ...

    assert (
        Ansi.clean(command.doc.help())
        == """\
USAGE
    command [-h] [val]

ARGUMENTS
    val          (default: 1)

OPTIONS
    --help (-h)  Displays this help message
"""
    )
