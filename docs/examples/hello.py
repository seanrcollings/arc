import arc


@arc.command
def hello(name: str):
    """Greets someone by name"""
    arc.print(f"Hello {name}!")


hello()
