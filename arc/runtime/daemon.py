from __future__ import annotations

import sys
import typing as t
from multiprocessing import connection
import socket

import arc
import arc.typing as at
from arc.runtime.server import Server

if t.TYPE_CHECKING:
    from arc.runtime.app import App


class Daemon:
    def __init__(self, app: App, address: at.Address) -> None:
        self.server = Server(app, address, daemon=False)
        self.address = address
        self.app = app

    def __call__(self, input: at.InputArgs = None) -> t.Any:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            server_started = s.connect_ex(self.address) == 0

        if server_started:
            self.app._setup_logger()
            self.app.logger.debug("Sending message to server process")
            input = input or sys.argv[1:]
            return self._send_message(input)
        else:
            self.server.start()

    def _send_message(self, input: at.InputArgs):
        client = connection.Client(self.address)
        client.send(input)
        res = client.recv()
        arc.print(res["stdout"], end="")
        arc.print(res["stderr"], end="")
        if res["error"]:
            arc.print("Error: ", res["error"])
        return res["result"]
