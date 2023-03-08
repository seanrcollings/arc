import arc


def dep(ctx: arc.Context) -> int:
    return 2


@arc.command()
def command(value: int = arc.Depends(dep)):
    arc.print(value)


command()
