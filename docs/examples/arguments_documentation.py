import arc

cli = arc.namespace("cli")


@cli.subcommand()
def command1(
    firstname: str = arc.Argument(description="Someone's first name"),
    lastname: str = arc.Option(default="", description="Someone's last name. Optional"),
    reverse: bool = arc.Flag(description="arc.print the name out in reverse"),
):
    """Documentation using descriptions"""


@cli.subcommand()
def command2(firstname, *, lastname="", reverse: bool):
    """Documentation in docstring

    # Arguments
    firstname: Someone's first name
    lastname: Someone's last name. Optional
    reverse: arc.print the name out in reverse
    """


cli()
