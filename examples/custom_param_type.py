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


class CircleParamType(ParamType):
    accepts = "Circle radius"  # used for error handling
    handles = Circle  # Marks it as the ParamType associated with Circle

    def convert(self, value: str):
        """
        The conversion method will get called with
        whatever data the user passed in. Then you can
        try and convert it to your type. If it's unsuccessful,
        call self.fail() with a user-friendly error message
        """
        if value.isnumeric():
            radius = int(value)
            return Circle(radius=radius)

        self.fail("radius must be a number")


cli = CLI()


@cli.command()
def circle(new_circle: Circle):
    """Displays some info about the circle object the command is passed"""
    print(new_circle)
    print(new_circle.circumference)


if __name__ == "__main__":
    cli()
