import sys

PREVIOUS_LINE = "\033[F"
CLEAR_LINE = "\033[K"


def write(string: str):
    sys.stdout.write(string)
