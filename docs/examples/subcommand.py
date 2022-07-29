import arc


@arc.command()
def command():
    print("hello there!")


@command.subcommand()
def sub1():
    print("This is sub 1")


@command.subcommand()
def sub2():
    print("This is sub 2")


command()
