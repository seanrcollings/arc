import arc

cli = arc.CLI()


@cli.command()
def c1():
    print("the first command")


@cli.command()
def c2():
    print("The second command")


cli()
