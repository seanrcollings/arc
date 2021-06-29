"""Provides classes to ask the users questions, and recieve back their answers"""
from .prompt import Prompt
from .questions import *


def confirm(message: str, *args, **kwargs) -> bool:
    """Request a Y/N answer from the user

    Args:
        message (str): Message to display to the user

    Returns:
        bool: The user's answer to the question
    """
    return Prompt(*args, **kwargs).confirm(message)
