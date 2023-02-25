import arc


@arc.command
def hello(firstname: str, lastname: str | None):
    name = firstname
    if lastname:
        name += f" {lastname}"

    arc.print(f"Hello, {name}! Hope you have a wonderful day!")


hello()
