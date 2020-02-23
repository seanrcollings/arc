from math import pi
from arc.converter import BaseConverter, ConversionError
from arc import CLI


# Custom Circle object
class Circle:
    def __init__(self, radius=3):
        self.radius = radius

    def __str__(self):
        return f"Circle({self.radius})"

    def get_circumference(self):
        return self.radius * 2 * pi


# Custom converter for Circle class
class CircleConverter(BaseConverter):
    convert_to = "Circle"

    @classmethod
    def convert(cls, value):
        '''
        The conversion method will get called with
        whatever data the user passed in. Then you can
        try and convert it to your type. If something fails,
        Raise a ConversionError and the BaseConverter will handle it
        will only convert to ints, a more expanded version might
        also convert to floats
        '''
        if value.isnumeric():
            radius = int(value)
            return Circle(radius=radius)

        raise ConversionError(value, cls.convert_to,
                              "Circle must be an whole number integer")


cli = CLI()
cli.config.converters["circle"] = CircleConverter


@cli.script("circle", ["<circle:new_circle>"])
def circle(new_circle):
    print(new_circle)
    print(new_circle.get_circumference())  # 31.41592653589793


cli()