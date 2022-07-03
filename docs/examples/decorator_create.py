import arc


@arc.decorator()
def cb(ctx):
    print("before execution")
    yield
    print("after execution")


@cb
@arc.command()
def command():
    print("command execution")


command()
