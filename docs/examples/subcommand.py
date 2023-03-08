import arc


@arc.command
def command():
    ...


@command.subcommand
def sub1():
    arc.print("This is sub 1")


@command.subcommand
def sub2():
    arc.print("This is sub 2")


command()
