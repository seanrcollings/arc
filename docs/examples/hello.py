import arc


@arc.command()
def hello(name: str):
    """My first arc program!"""
    print(f"Hello {name}!")


hello()
