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

    @arc.command()
    def other_sub():
        return "other_sub"

    ns.add_command(other_sub, ["os"])

    assert ns("sub") == "sub"
    assert ns("s") == "sub"
    assert ns("other-sub") == "other_sub"
    assert ns("os") == "other_sub"


def test_global_args():
    @arc.command()
    def command(state: arc.State, *, val, val2):
        state["val"] = val
        state.val2 = val2

    @command.subcommand()
    def sub(state: arc.State):
        return state

    assert command("--val 2 --val2 2 sub") == arc.State(val="2", val2="2")
