import arc


@arc.command
def command():
    arc.print("We're going to throw an error")
    raise RuntimeError("Something has gone wrong!")


@command.handle(Exception)
def handle_exception(ctx: arc.Context, exc):
    arc.print("General exception handler")


@command.handle(RuntimeError)
def handle_runtime_error(ctx: arc.Context, exc):
    arc.print("Cannot handle this error, bubbling")
    raise exc


command()
