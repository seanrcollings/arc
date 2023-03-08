import arc
from arc.color import fg
from arc.present import Box


@arc.command()
def command():
    arc.print(Box("Some cool text", padding=2, color=fg.GREEN))


command()
