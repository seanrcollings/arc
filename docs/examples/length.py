from typing import Annotated
import arc
from arc.types.middleware import Len


@arc.command()
def command(vals: Annotated[list[int], Len(2, 10)]):
    arc.print(vals)


command()
