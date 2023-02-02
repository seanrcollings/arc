import pytest
import arc
from arc import errors

# NOTE: any time that cli_params is checked against, two are added to the explcit number
# to account for --help and --autocomplete


def test_group():
    @arc.group
    class Group:
        val: int
        other_val: int

    @arc.command()
    def command(group: Group):
        return group

    assert len(list(command.cli_params)) == 3
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

    assert len(list(command.cli_params)) == 3

    group = command("1 2")
    assert group.val == 1
    assert group.sub.other_val == 2


def test_dependencies():
    def depfunc1():
        return 1

    def depfunc2():
        return 2

    @arc.group
    class Group:
        dep1 = arc.Depends(depfunc1)
        dep2 = arc.Depends(depfunc2)
        ctx: arc.State

    @arc.command()
    def command(group: Group):
        return group

    group = command("", state={"val": 1})

    assert group.dep1 == 1
    assert group.dep2 == 2
    assert isinstance(group.ctx, arc.State)


def test_non_unique_names():
    @arc.group
    class Group:
        value: int

    with pytest.raises(errors.ParamError):

        @arc.command()
        def command(value: int, group: Group):
            print(value)
