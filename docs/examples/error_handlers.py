import arc


@arc.command()
def command():
    raise RuntimeError("Something has gone wrong!")


@command.handle(RuntimeError)
def handle_exception(exc, context):
    print("handled!")


command()