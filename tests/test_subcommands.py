import arc


def test_subcommand():
    ns = arc.namespace("ns")

    @ns.subcommand
    def sub():
        return "sub"

    assert ns("sub") == "sub"


def test_aliases():
    ns = arc.namespace("ns")

    @ns.subcommand("sub", "s")
    def sub():
        return "sub"

    @arc.command
    def other_sub():
        return "other_sub"

    ns.subcommand(other_sub, "os")

    assert ns("sub") == "sub"
    assert ns("s") == "sub"
    assert ns("other-sub") == "other_sub"
    assert ns("os") == "other_sub"


def test_creation_conventions():
    ns = arc.namespace("ns")

    @ns.subcommand
    def sub1():
        return True

    def sub2():
        return True

    ns.subcommand(sub2)

    @ns.subcommand
    def sub3():
        return True

    @ns.subcommand("changed-name")
    def sub4():
        return True

    assert ns("sub1")
    assert ns("sub2")
    assert ns("sub3")
    assert ns("changed-name")
