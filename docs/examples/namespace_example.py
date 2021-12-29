import arc

cli = arc.CLI()


@arc.command()
def n1(ctx: arc.Context):
    print(ctx.command.get_help(ctx))
    ctx.exit(1)


@n1.subcommand()
def sub():
    print("n1:sub")


n2 = arc.namespace("n2")


@n2.subcommand()
def sub2():
    print("n2:sub2")


cli.install_commands(n1, n2)

cli()
