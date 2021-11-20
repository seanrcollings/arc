from math import pi
from arc.types import ParamType
from arc import CLI


class Circle:
    def __init__(self, radius=3):
        self.radius = radius

    def __str__(self):
        return f"Circle(radius: {self.radius})"

    @property
    def circumference(self):
        return self.radius * 2 * pi

    @classmethod
    def __convert__(cls, value: str, param_type: ParamType):
        """
        The conversion method will get called with
        whatever data the user passed in. Then you can
        try and convert it to your type. If it's unsuccessful,
        call self.fail() with a user-friendly error message
        """
        print("--- Circle Conversion ---")
        if value.isnumeric():
            radius = int(value)
            return Circle(radius=radius)

        param_type.fail("radius must be a number")

    def __cleanup__(self):
        """Arc will call this method after the command exits.
        Use it to cleanup any open resources (like files, or network
        connections) or simply some exiting code. This method
        is optional.
        """
        print("--- Circle cleanup ---")


cli = CLI()


@cli.command()
def circle(new_circle: Circle):
    """Displays some info about the circle object the command is passed"""
    print(new_circle)
    print(new_circle.circumference)


if __name__ == "__main__":
    cli()
