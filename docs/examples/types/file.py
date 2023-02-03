import arc
from arc.types import File


@arc.command()
def command(file: File.Read):
    arc.print(file.readline())


command()
