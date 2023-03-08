import re
import arc
from arc import color
from arc.types import File


@arc.command
def grep(pattern: re.Pattern, files: list[File.Read]):
    for file in files:  # Iterate over all the files
        for line in file.readlines():  # Iterate over all the line in the file
            if match := pattern.search(line):  # check for a match
                # If there is a match, highlight it
                colored = pattern.sub(
                    color.fg.RED + match.group() + color.fx.CLEAR,
                    line,
                )
                arc.print(colored, end="")


grep()
