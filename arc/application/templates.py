cli = """\
from arc import CLI, ExecutionError

cli = CLI(name="{name}")


@cli.command()
def command():
    print("Hello there!")


cli()
"""

context = """\
from arc import Context

class {class_name}Context(Context):
    ...
"""


templates = {
    "cli": cli,
    "context": context,
}
