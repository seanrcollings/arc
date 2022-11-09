import arc


def get_default_name():
    return "Josuke"


@arc.command()
def command(name: str = arc.Argument(get=get_default_name)):
    arc.print(f"Good morning {name}")


command()
