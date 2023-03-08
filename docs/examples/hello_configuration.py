import arc
from arc import color

arc.configure(
    version="1.0.0",
    color=arc.ColorConfig(accent=color.fg.RED),
)


@arc.command
def hello(name: str):
    """My first arc program!"""
    arc.print(f"Hello {name}!")


hello()
