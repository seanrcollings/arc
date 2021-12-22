import arc


@arc.command()
def hello(firstname=arc.Option(), lastname=arc.Option(default="")):
    print(f"Hello, {firstname} {lastname}! Hope you have a wonderful day!")


hello()
