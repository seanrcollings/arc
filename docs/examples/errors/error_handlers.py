import arc


@arc.command
def command():
    arc.print("We're going to throw an error")
    raise RuntimeError("Something has gone wrong!")


@command.handle(RuntimeError)
def handle_exception(ctx: arc.Context, exc):
    arc.print("handled!")


command()
