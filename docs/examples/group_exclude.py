import arc


@arc.group(exclude=["val2"])
class Group:
    val1: str
    val2: str


@arc.command()
def command(group: Group):
    ...


command()
