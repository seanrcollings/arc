import arc


@arc.command()
def hello(firstname=arc.Argument(), repeat: int = arc.Count()):
    arc.print(f"Repeat {repeat} time(s)")
    for i in range(0, repeat):
        arc.print(f"Hello, {firstname}! Hope you have a wonderful day!")


hello()
