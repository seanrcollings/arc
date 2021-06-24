from math import pi
from arc.convert import BaseConverter, ConversionError, register
from arc import CLI


# Custom Circle object
class Circle:
    def __init__(self, radius=3):
        self.radius = radius

    def __str__(self):
        return f"Circle(radius: {self.radius})"

    def get_circumference(self):
        return self.radius * 2 * pi


# Custom converter for Circle class
@register(Circle)
class CircleConverter(BaseConverter):
    def convert(self, value: str):
        """
        The conversion method will get called with
        whatever data the user passed in. Then you can
        try and convert it to your type. If something fails,
        Raise a ConversionError and the BaseConverter will handle it
        will only convert to ints, a more expanded version might
        also convert to floats
        """
        if value.isnumeric():
            radius = int(value)
            return Circle(radius=radius)

        raise ConversionError(value, expected="A whole number radius")


cli = CLI()


@cli.command()
def circle(new_circle: Circle):
    """Displays some info about the circle object the command is passed"""
    print(new_circle)
    # print(new_circle.get_circumference())


if __name__ == "__main__":
    cli()
