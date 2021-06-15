from .prompt import Prompt
from .questions import *


def confirm(message: str, *args, **kwargs):
    return Prompt(*args, **kwargs).confirm(message)
