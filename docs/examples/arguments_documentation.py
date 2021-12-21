from arc import CLI, Argument, Option, Flag

cli = CLI()


@cli.command()
def command1(
    firstname: str = Argument(description="Someone's first name"),
    lastname: str = Option(default="", description="Someone's last name. Optional"),
    reverse: bool = Flag(description="Print the name out in reverse"),
):
    """Documentation using descriptions"""


@cli.command()
def command2(firstname, *, lastname="", reverse: bool):
    """Documentation in docstring

    # Arguments
    firstname: Someone's first name
    lastname: Someone's last name. Optional
    reverse: Print the name out in reverse
    """


cli()
