import arc


@arc.command()
def command():
    print("command execution")


@command.callback()
def callback(args: dict, ctx: arc.Context):
    print("before execution")
    yield
    print("after execution")


command()