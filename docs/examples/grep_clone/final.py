import re
import arc
from arc import color
from arc.types import File


@arc.command()
def grep(pattern: re.Pattern, files: list[File.Read]):
    for file in files:
        for line in file.readlines():
            if match := pattern.search(line):
                colored = pattern.sub(
                    color.fg.RED + match.group() + color.effects.CLEAR,
                    line,
                )
                print(colored, end="")


grep()
