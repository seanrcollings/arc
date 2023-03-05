import arc
from arc.prompt import Prompt


@arc.command()
def hello(prompt: Prompt):
    name = prompt.input("Name: ")

    while not prompt.confirm("Are you sure?"):
        name = prompt.input("Name: ")

    print(f"Hello, {name}!")


hello()
