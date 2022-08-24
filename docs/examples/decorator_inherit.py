import arc


@arc.decorator(children_only=True)
def cb():
    arc.print("-------before execution-------")
    yield
    arc.print("-------after execution-------")


@cb
@arc.command()
def command():
    ...


@command.subcommand()
def sub():
    arc.print("Execution")


command()
