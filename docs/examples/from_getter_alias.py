import arc


@arc.command
def command(name: str = arc.Argument()):
    arc.print(f"Good morning {name}")


@command.get("name")
def get_default_name():
    return "Josuke"


command()
