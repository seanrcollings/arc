from enum import Enum
import arc


class Color(Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


@arc.command
def paint(color: Color):
    if color is Color.RED:
        arc.print("You painted the walls the bloodiest of reds")
    elif color is Color.YELLOW:
        arc.print("You painted the walls the most fabulous yellow")
    else:
        arc.print("You painted the walls the deepest of greens")


paint()
