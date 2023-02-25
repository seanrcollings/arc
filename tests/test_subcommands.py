import arc


def test_subcommand():
    ns = arc.namespace("ns")

    @ns.subcommand()
    def sub():
        return "sub"

    assert ns("sub") == "sub"


def test_aliases():
    ns = arc.namespace("ns")

    @ns.subcommand("sub", "s")
    def sub():
        return "sub"

    @arc.command()
    def other_sub():
        return "other_sub"

    ns.subcommand(other_sub, "os")

    assert ns("sub") == "sub"
    assert ns("s") == "sub"
    assert ns("other-sub") == "other_sub"
    assert ns("os") == "other_sub"
