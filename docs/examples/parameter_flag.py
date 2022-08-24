import arc


@arc.command()
def hello(firstname: str, reverse: bool):
    if reverse:
        firstname = firstname[::-1]

    arc.print(f"Hello, {firstname}! Hope you have a wonderful day!")


hello()
