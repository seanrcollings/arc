class BaseConverter:
    def __new__(cls, value):
        return cls.convert(value)

    @property
    def convert(self):
        raise NotImplementedError(
            "Must Implement convert method in child class")

    @property
    def convert_to(self):
        raise NotImplementedError(
            "Must Implement convert_to string for documentation")
