from arc import CLI, Utility

converse = Utility("converse")
cli = CLI(utilities=[converse])
# can also use cli.install_utilities(converse) for the same effect


# regular cli command
@cli.script("greet")
def cli_greet(name="Joseph Joestar"):
    """Command that greets someone CLI command"""
    print(f"Hello, {name}!")
    print("This command is associated with the global CLI")


# utility command
@converse.script("greet")
def utility_greet(name="Jotaro Kujo"):
    """Command that greets someone utility command"""
    print(f"Howdy, {name}!")
    print("This command is associated with the 'converse' utility")


if __name__ == "__main__":
    cli()
