import arc


@arc.command
def hello(firstname: str, lastname: str = "Joestar"):
    name = f"{firstname} {lastname}"
    arc.print(f"Hello, {name}! Hope you have a wonderful day!")


hello()
