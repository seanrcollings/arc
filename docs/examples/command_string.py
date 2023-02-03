import arc


@arc.command()
def hello(name: str):
    arc.print(f"Hello {name}!")


hello("Sean")
