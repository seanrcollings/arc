import time
import arc
from arc.runtime.serve import Server
from arc.present.console import Console
from arc.prompt.prompt import Prompt

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


@command.subcommand
def expected_error() -> None:
    raise arc.ExecutionError("Expected error")


@command.subcommand
def unexpected_error() -> None:
    raise Exception("Unexpected error")


@command.subcommand
def name(prompt: Prompt):
    name = input("What is your name? ")
    arc.print(f"Hello, {name}!")


app = arc.App(command)

app.serve(("localhost", 6001))
