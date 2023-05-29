from typing import Annotated
import arc
from arc import types
import datetime


@arc.command
def command(date: Annotated[datetime.datetime, types.DateTimeArgs("%Y-%m-%d")]):
    arc.print(date)


command()
