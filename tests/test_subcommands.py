import pytest

import arc


def test_subcommand():
    ns = arc.namespace("ns")

    @ns.subcommand()
    def sub():
        return "sub"

    assert ns("sub") == "sub"


def test_aliases():
    ns = arc.namespace("ns")

    @ns.subcommand(("sub", "s"))
    def sub():
        return "sub"

    assert ns("sub") == "sub"
    assert ns("s") == "sub"


def test_global_args():
    @arc.command()
    def command(state: arc.types.State, *, val, val2):
        state["val"] = val
        state.val2 = val2

    @command.subcommand()
    def sub(state: arc.types.State):
        return state

    assert command("--val 2 --val2 2 sub") == arc.types.State(val="2", val2="2")
