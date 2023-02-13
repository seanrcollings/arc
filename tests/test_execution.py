import arc


class TestNestedExecution:
    def test_sub_execution(self):
        @arc.command()
        def command():
            ...

        @command.subcommand()
        def sub1(ctx: arc.Context):
            return ctx.execute(sub2)

        @command.subcommand()
        def sub2(val: int = 1):
            return val

        @command.subcommand()
        def sub3(ctx: arc.Context):
            return ctx.execute(sub2, val=10)

        assert command("sub1") == 1
        assert command("sub2") == 1
        assert command("sub3") == 10

    def test_group_execution(self):
        @arc.command()
        def command():
            ...

        @command.subcommand()
        def sub1(ctx: arc.Context):
            return ctx.execute(sub2, val=10)

        @arc.group
        class Group:
            val: int = 1

        @command.subcommand()
        def sub2(group: Group):
            return group.val

        assert command("sub1") == 10
        assert command("sub2") == 1
