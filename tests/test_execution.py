import arc


class TestNestedExecution:
    def test_sub_execution(self):
        @arc.command
        def command():
            ...

        @command.subcommand
        def sub1(ctx: arc.Context):
            return ctx.execute(sub2)

        @command.subcommand
        def sub2(val: int = 1):
            return val

        @command.subcommand
        def sub3(ctx: arc.Context):
            return ctx.execute(sub2, val=10)

        assert command("sub1") == 1
        assert command("sub2") == 1
        assert command("sub3") == 10

    def test_group_execution(self):
        @arc.group
        class Group:
            val: int = 1

        command = arc.namespace("command")

        @command.subcommand
        def sub1(group: Group):
            return group.val

        @command.subcommand
        def sub2(ctx: arc.Context):
            return ctx.execute(sub1, val=10)

        @command.subcommand
        def sub3(ctx: arc.Context, group: Group):
            return ctx.execute(sub1, group=group)

        @command.subcommand
        def sub4(ctx: arc.Context):
            return ctx.execute(sub1)

        assert command("sub1") == 1
        assert command("sub1 15") == 15
        assert command("sub2") == 10
        assert command("sub3 15") == 15
        assert command("sub4") == 1
