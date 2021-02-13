from arc import CLI, namespace

cli = CLI()
converse = namespace("converse")
cli.install_command(converse)


# regular cli command
@cli.command("greet")
def cli_greet(name="Joseph Joestar"):
    """Command that greets someone -- CLI command"""
    print(f"Hello, {name}!")
    print("This command is associated with the global CLI")


# subcommand
@converse.subcommand("greet")
def utility_greet(name="Jotaro Kujo"):
    """Command that greets someone -- subcommand"""
    print(f"Howdy, {name}!")
    print("This command is associated with the 'converse' command")


if __name__ == "__main__":
    cli()
