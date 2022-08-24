import re
import arc
from arc import types


@arc.command()
def command(pattern: re.Pattern, files: list[types.File.Read]):
    arc.print(pattern)
    arc.print(files)


command()
