from arc import CLI

cli = CLI()


@cli.callback()
def global_callback(args, ctx):
    print("global callback -- start")
    yield
    print("global callback -- end")


@cli.command()
def c1():
    print("c1")


@c1.callback()
def c1_callback(args, ctx):
    print("c1 callback -- start")
    yield
    print("c1 callback -- end")


@c1.subcommand()
def sub():
    print("c1:sub")


@cli.command()
def c2():
    print("c2")


cli()