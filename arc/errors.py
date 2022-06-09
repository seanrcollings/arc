class Exit(SystemExit):
    ...


class ArcError(Exception):
    ...


class ExternalError(ArcError):
    """Errors that fire due to user / input errors"""


class ArgumentError(ExternalError):
    ...


class ConversionError(ArgumentError):
    """Raised if a type conversion fails"""

    def __init__(self, value, message: str, source=None):
        self.value = value
        self.source = source
        super().__init__(message)


class InternalError(ArcError):
    """Errors that fire due to development / internal errors"""


class ParamError(InternalError):
    def __init__(self, message, param):
        super().__init__(message)
        self.param = param
