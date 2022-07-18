import typing as t
import re
from arc import errors


class Matches:
    """Validator to match a regular expression.

    ## Type Constraints
    - Matches against `str(value)`, so the type must have a sensible string representation
    """

    def __init__(self, pattern: str | re.Pattern[str], flags: int = 0):
        self.pattern = pattern
        self.flags = flags

    def __call__(self, value: t.Any):
        if not re.match(self.pattern, str(value), self.flags):
            raise errors.ValidationError(
                f"does not match expected format: {self.pattern}"
            )

        return value
