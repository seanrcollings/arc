'''Base CLI example'''
from arc import CLI
cli = CLI()


@cli.script("greet", options=["name"])
def greet(name="Joseph Joestar"):
    '''Command that greets someone'''
    print(f"Hello, {name}!")