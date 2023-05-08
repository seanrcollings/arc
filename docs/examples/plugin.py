import arc


def plugin(ctx: arc.Context):
    command = ctx.root

    @command.use
    def middleware(ctx: arc.Context):
        arc.print("Starting plugin middleware!")
        yield
        arc.print("Ending plugin middleware!")

    @command.subcommand
    def subcommand():
        arc.print("Subcommand installed by plugin!")
