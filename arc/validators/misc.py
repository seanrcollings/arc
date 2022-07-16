import typing as t
import re
from arc import errors


class Matches:
    def __init__(self, pattern: str | re.Pattern[str]):
        self.pattern = pattern

    def __call__(self, value: t.Any):
        if not re.match(self.pattern, str(value)):
            raise errors.ValidationError(
                f"does not follow required format: {self.pattern}"
            )

        return value
