import arc


@arc.command()
def command():
    ...


@command.subcommand()
def sub1():
    print("This is sub 1")


@sub1.subcommand()
def nested1():
    print("This is nested 1")


@command.subcommand()
def sub2():
    print("This is sub 2")


@sub2.subcommand()
def nested2():
    print("This is nested 2")


command()
