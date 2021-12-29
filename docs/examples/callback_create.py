import arc
from arc import callback


@callback.create()
def cb(args, ctx):
    print("before execution")
    yield
    print("after execution")


@cb
@arc.command()
def command():
    print("command execution")


command()