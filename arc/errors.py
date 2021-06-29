from typing import Optional
from arc.color import fg, effects


class ArcError(Exception):
    """Base Arc Exception"""

    def __init__(self, *args):
        super().__init__()
        self.message = " ".join(args)

    def __str__(self):
        return self.message

    # @staticmethod
    # def colorize(string: str):
    #     return f"{fg.RED}{string}{effects.CLEAR}"


class ExecutionError(ArcError):
    """Raised if there is a problem during the execution of a command"""


class NoOpError(ExecutionError):
    """Sepcial Execution to raise when
    the specific namespace CANT be executed"""


class CommandError(ArcError):
    """Raised when there is an error in the creation of a command"""


class ValidationError(ArcError):
    """Raised when there is an error in validating command input or in a validator callback"""


class ActionError(ArcError):
    """Raised when a action callback fails to execute"""


class TokenizerError(ArcError):
    def __init__(self, token, mode):
        self.token = token
        super().__init__(f"Unable to understand: `{self.token}` in command string")


class ParserError(ArcError):
    """Raised when there is an error parsing the token stream"""


class ConversionError(ArcError):
    """Raised if a type conversion fails """

    def __init__(self, value, expected: str, helper_text: str = ""):
        """Initializes the conversion errors
        :param value: the value attempting to be converted
        :param expected: string describing what the value should be
        :param helper_text: any additional helper text for the user
        """
        self.value = value
        self.expected = expected
        self.helper_text = helper_text

        super().__init__(f"\nValue: {value}\nExpected: {expected}\nInfo: {helper_text}")
