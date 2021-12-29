import arc

cli = arc.CLI()


@cli.command()
def c1():
    """First command"""
    print("the first command")


@cli.command()
def c2():
    """Second command"""
    print("The second command")


cli()
