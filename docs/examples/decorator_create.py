import arc


@arc.decorator()
def cb(ctx):
    arc.print("before execution")
    yield
    arc.print("after execution")


@cb
@arc.command()
def command():
    arc.print("command execution")


command()
