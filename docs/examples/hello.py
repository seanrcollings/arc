import arc


@arc.command()
def hello(name: str):
    """My first arc program!"""
    arc.print(f"Hello {name}!")


hello()
