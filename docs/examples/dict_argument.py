import arc


@arc.command()
def command(numbers: dict[str, int]):
    arc.print(numbers)


command()
