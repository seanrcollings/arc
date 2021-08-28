"""Base CLI example"""
from arc import CLI

cli = CLI()  # Create an instance of the Arc CLI


# Specifies the command's name (if not specified, will use the function's name)
@cli.command()
def greet(*, name="Joseph Joestar"):
    # any options specified above will be passed
    # to the function with the same name.
    # Since it's given a default value, it's optional
    """Command that greets someone"""  # Docstrings are used for the 'help' command
    # Command body
    print(f"Hello, {name}!")


if __name__ == "__main__":
    cli()  # Run the CLI
