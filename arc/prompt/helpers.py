from typing import Literal
import sys

PREVIOUS_LINE = "\033[F"


def clear_line(amount: Literal["all", "before", "after"] = "all"):
    if amount == "all":
        num = 2
    elif amount == "before":
        num = 1
    else:
        num = 0

    return f"\033[{num}K"


def write(string: str):
    sys.stdout.write(string)
