from typing import Annotated
import arc


def round2(val: float):
    return round(val, 2)


@arc.command()
def command(val: Annotated[float, round2]):
    arc.print(val)


command()
