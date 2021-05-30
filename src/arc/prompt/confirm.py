import sys
from arc.color import fg, effects

PREVIOUS_LINE = "\033[F"
CLEAR_LINE = "\033[K"


def write(string: str):
    sys.stdout.write(string)


def confirm(message: str):
    result = {
        "y": True,
        "n": False,
    }
    print(f"{message} [{fg.GREEN}Y{effects.CLEAR}/{fg.RED}N{effects.CLEAR}]")
    while True:
        user_input = input(f"\n{CLEAR_LINE}> ").lower()
        if user_input in result:
            return result[user_input]
        write(
            f"{PREVIOUS_LINE}{PREVIOUS_LINE}Not valid, please enter "
            f"{fg.GREEN}y{effects.CLEAR} or {fg.RED}n{effects.CLEAR}",
        )
