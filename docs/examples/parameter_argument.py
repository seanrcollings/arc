import arc


@arc.command()
def hello(firstname=arc.Argument(), lastname=arc.Argument(default="")):
    arc.print(f"Hello, {firstname} {lastname}! Hope you have a wonderful day!")


hello()
