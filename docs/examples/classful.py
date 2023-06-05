import arc


@arc.command
class hello:
    """Greets a person by name"""

    name: str = arc.Argument(desc="Name of the person to greet", default="world")

    def handle(self):
        arc.print(f"Hello, {self.name}!")


hello()
