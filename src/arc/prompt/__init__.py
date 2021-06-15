from .prompt import Prompt
from .questions import *


def confirm(message: str):
    return Prompt().ask(ConfirmQuestion(message))
