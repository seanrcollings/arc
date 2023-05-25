from arc.types.type_arg import TypeArg
from arc.types.default import Default


class DateTimeArgs(TypeArg):
    __slots__ = ("format",)

    def __init__(self, format: str = Default("%Y-%m-%dT%H:%M:%S")):
        self.format = format


class DateArgs(TypeArg):
    __slots__ = ("format",)

    def __init__(self, format: str = Default("%Y-%m-%d")):
        self.format = format


class TimeArgs(TypeArg):
    __slots__ = ("format",)

    def __init__(self, format: str = Default("%H:%M:%S")):
        self.format = format
