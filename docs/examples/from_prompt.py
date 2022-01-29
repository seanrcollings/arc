import arc


@arc.command()
def command(name: str = arc.Argument(prompt="What is your first name?")):
    print("Hello, " + name)


command()