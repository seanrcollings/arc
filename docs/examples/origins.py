import arc


@arc.command()
def command(ctx: arc.Context, value: int = 2):
    origin = ctx.get_origin("value")
    arc.print(value, origin)


command()
