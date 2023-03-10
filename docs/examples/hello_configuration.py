import arc

arc.configure(version="1.0.0")


@arc.command
def hello(name: str):
    """My first arc program!"""
    arc.print(f"Hello {name}!")


hello()
