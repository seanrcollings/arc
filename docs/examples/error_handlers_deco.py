import arc


@arc.decorator()
def handle_exception(context):
    try:
        yield
    except RuntimeError:
        arc.print("handled!")


@handle_exception
@arc.command()
def command():
    raise RuntimeError("Something has gone wrong!")


command()
