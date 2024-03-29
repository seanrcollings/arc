from enum import Enum
import arc

arc.configure(autocomplete=True)


class Color(Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


# Could also use:
# Color = Literal["red", "yellow", "green"]


@arc.command
def paint(color: Color):
    if color is Color.RED:
        arc.print("You painted the walls the bloodiest of reds")
    elif color is Color.YELLOW:
        arc.print("You painted the walls the most fabulous yellow")
    else:
        arc.print("You painted the walls the deepest of greens")


paint()
