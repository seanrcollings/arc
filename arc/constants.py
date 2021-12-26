from arc import utils

NAMESPACE_SEP: str = ":"
"""Character to seperate command names: `parent:child:granchild`"""
FLAG_PREFIX: str = "--"
"""Characters the proceed a flag argument: `--flag`"""
SHORT_FLAG_PREFIX: str = "-"
"""Characters that proceed a shortened flag `-f`"""


class MissingType:
    def __repr__(self):
        return "MISSING"


MISSING = MissingType()
"""Represents a missing value.
Used to represent an argument with no default value"""
