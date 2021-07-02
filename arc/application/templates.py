cli = """\
from arc import CLI, ExecutionError, ParsingMethod

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

callbacks = """\
from arc import callbacks
from arc.errors import ValidationError

@callbacks.before
def before_example(args):
    print(args)

"""

templates = {
    "cli": cli,
    "context": context,
    "callbacks": callbacks,
}
