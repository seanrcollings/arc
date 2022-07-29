import arc


@arc.command()
def add(val1: int, val2: int):
    arc.print(f"The answer is: {val1 + val2}")


add()
