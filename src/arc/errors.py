from arc.color import fg, effects


class ArcError(Exception):
    """Base Arc Exception"""

    def __init__(self, *args):
        super().__init__()
        self.message = self.colorize(" ".join(args))

    def __str__(self):
        return self.message

    @staticmethod
    def colorize(string: str):
        return f"{fg.RED}{string}{effects.CLEAR}"


class ExecutionError(ArcError):
    """Raised if there is a problem during the execution of a command"""


class CommandError(ArcError):
    """Raised when there is an error in the creation of a command"""


class ValidationError(ArcError):
    """Raised when there is an error in validating command input"""


class TokenizerError(ArcError):
    def __init__(self, token, mode):
        self.token = token
        super().__init__(f"Couldn't match on token: `{self.token}` in {mode}")


class ParserError(ArcError):
    """Raised when there is an error parsing the token stream"""


class ConversionError(ArcError):
    """Raised if a type conversion fails """

    def __init__(self, value, helper_text=None, message=None):
        """Initializes the conversion errors
        :param value: the value attempting to be converted
        :param helper_text: any additional helper text for the user
        """
        if message:
            super().__init__(message)
        else:
            super().__init__(f"Value: {value}\nInfo:{helper_text}")
        self.value = self.colorize(value)
        self.helper_text = self.colorize(helper_text)
