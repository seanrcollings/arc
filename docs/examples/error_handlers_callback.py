import arc


@arc.command()
def command():
    raise RuntimeError("Something has gone wrong!")


@command.callback
def handle_exception(args, context):
    try:
        yield
    except RuntimeError as exc:
        print("handled!")


command()