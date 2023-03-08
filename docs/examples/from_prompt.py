import arc


@arc.command
def command(name: str = arc.Argument(prompt="What is your first name? ")):
    arc.print("Hello, " + name)


command()
