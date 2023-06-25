import sys
import arc.typing as at
from arc.runtime.serve import Client
from arc.runtime.serve.messages import (
    Close,
    Output,
    CommandResult,
    Exit,
    Ping,
    RunCommand,
    Error,
)

import arc
from numpy import isin


class Repl:
    def __init__(self, address: at.Address) -> None:
        self.address = address

    def run(self) -> None:
        print("Server REPL")
        with Client(self.address) as client:
            while True:
                command = input(">>> ")
                should_exit = self._handle_command(client, command)

                if should_exit:
                    break

    def _handle_command(self, client: Client, command: str) -> bool:
        match command:
            case "exit":
                client.send(Exit())
                return True
            case "close":
                client.send(Close())
                return True
            case "ping":
                self._ping_command(client)
            case s if s.startswith("run"):
                return self._run_command(client, s[3:].strip())
            case "help" | "?":
                print("COMMANDS")
                print(
                    "  close - Closes the connection to the server and exits the REPL"
                )
                print("  exit - Stops to server and exits the REPL")
                print("  ping - Pings the server to check if it is alive")
                print("  run <command> - Runs a command on the server")
            case s:
                print(f"Unknown command {s!r}")

        return False

    def _ping_command(self, client: Client) -> None:
        client.send(Ping())
        res = client.recv()
        print(res)

    def _run_command(self, client: Client, command: str) -> bool:
        client.send(RunCommand(command))

        while True:
            res = client.recv()

            if isinstance(res, CommandResult):
                break

            if isinstance(res, Error):
                arc.err(res.error)
                break

            assert isinstance(res, Output)

            if res.stream == "stdout":
                sys.stdout.write(res.output)
            else:
                sys.stderr.write(res.output)

        if isinstance(res, CommandResult):
            arc.print(f"Result: {res.result}")
            return False
        else:
            arc.err(f"Command failed: {res.error}")
            return True
