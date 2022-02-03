import arc
import os

os.environ["VAL"] = "2"


@arc.command()
def command(val: int = arc.Argument(envvar="VAL")):
    print(f"VAL: {val}")


command()
