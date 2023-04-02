import arc


@arc.command
def cli(
    firstname: str = arc.Argument(desc="Someone's first name"),
    lastname: str = arc.Option(default="Johnson", desc="Someone's last name. Optional"),
    reverse: bool = arc.Flag(desc="print the name out in reverse"),
):
    """Parameter documentation"""


cli()
