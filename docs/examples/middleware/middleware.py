import arc


@arc.command
def hello(name: str = "world"):
    arc.print(f"Hello, {name}!")


@hello.use
def middleware(ctx: arc.Context):
    arc.print("Hello from middleware!")
    arc.print(f"Command name: {ctx.command.name}")
    arc.print(f"Command args: {ctx['arc.args']}")


hello()
