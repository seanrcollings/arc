from arc import CLI

cli = CLI()


@cli.command()
def command():
    print("command")


@command.subcommand()
def sub():
    print("command:sub")


@sub.subcommand()
def sub2():
    print("command:sub:sub2")


cli()
