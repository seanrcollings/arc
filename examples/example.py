'''Base CLI example'''
from arc import CLI
cli = CLI()  # Create an instance of the Arc CLI


# Specifies the command's name and it's available options
@cli.script("greet", options=["name"])
def greet(name="Joseph Joestar"):
    # any options specified above will be passed
    # to the function with the same name.
    # Since it's given a default value, it's optional
    '''Command that greets someone'''  # Docstrings are used for the 'help' command
    # Script body
    print(f"Hello, {name}!")


cli()  # Run the CLI
