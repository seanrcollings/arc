import time
import arc
from arc.runtime.serve import Server

from arc.present.console import Console

arc.configure(debug=True)


@arc.command
def command() -> None:
    arc.print("Start 1", flush=True)
    time.sleep(10)
    arc.print("End 1", flush=True)


@command.subcommand
def sub() -> None:
    arc.print("Start 2", flush=True)
    time.sleep(10)
    arc.print("End 2", flush=True)


app = arc.App(command)

app.serve(("localhost", 6001))
