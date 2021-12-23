import arc


@arc.command()
def command(numbers: dict[str, int]):
    print(numbers)


command()
