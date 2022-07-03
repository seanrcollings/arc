from enum import Enum
import arc


class Color(Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


@arc.command()
def paint(color: Color = arc.Argument()):
    if color == Color.RED:
        print("You painted the walls the bloodiest of reds")
    elif color == Color.YELLOW:
        print("You painted the walls the most fabulous yellow")
    else:
        print("You painted the walls the deepest of greens")


paint()
