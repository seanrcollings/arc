import pytest
import arc


def test_group():
    @arc.group
    class Group:
        val: int
        other_val: int

    @arc.command()
    def command(group: Group):
        return group

    assert len(list(command.cli_params)) == 2
    group = command("1 2")
    assert group.val == 1
    assert group.other_val == 2


def test_subgroup():
    @arc.group
    class Sub:
        other_val: int

    @arc.group
    class Group:
        val: int
        sub: Sub

    @arc.command()
    def command(group: Group):
        return group

    assert len(list(command.cli_params)) == 2

    group = command("1 2")
    assert group.val == 1
    assert group.sub.other_val == 2


def test_depenancies():
    def depfunc1(ctx):
        return 1

    def depfunc2(ctx):
        return 2

    @arc.group
    class Group:
        dep1 = arc.Depends(depfunc1)
        dep2 = arc.Depends(depfunc2)
        ctx: arc.Context

    @arc.command()
    def command(group: Group):
        return group

    group = command("")

    assert group.dep1 == 1
    assert group.dep2 == 2
    assert isinstance(group.ctx, arc.Context)
