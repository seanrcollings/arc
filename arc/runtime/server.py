from __future__ import annotations
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import logging
from multiprocessing import connection
import os
import socket
import sys
import typing as t

import arc
from arc import typing as at
from arc.logging import formatter


if t.TYPE_CHECKING:
    from arc.runtime.app import App


class ServerStringIO(StringIO):
    def isatty(self) -> bool:
        return True


class Server:
    def __init__(
        self, app: App, address: tuple[str, int], daemon: bool = False
    ) -> None:
        self.app = app
        self.address = address
        self.daemon = daemon
        self._running = False

    def start(self):
        logger = logging.getLogger("arc.serve")
        self.app.logger = logger
        self.app._setup_logger()
        self._running = True

        if self.daemon:
            self.app.logger.debug("Starting daemon process")
            pid = os.fork()
            if pid == 0:
                self._listen()
        else:
            self.app.logger.debug("Starting server")
            self._listen()

    def _listen(self) -> None:
        listener = connection.Listener(self.address)

        stdout = ServerStringIO()
        stderr = ServerStringIO()
        handler = logging.StreamHandler(stderr)
        handler.setFormatter(formatter)
        # self.app.logger.addHandler(handler)

        with redirect_stderr(stderr), redirect_stdout(stdout):
            while self._running:
                with listener.accept() as conn:
                    if conn.poll():
                        try:
                            msg = conn.recv()
                            self.app.logger.debug(f"Server got message: {msg}")

                            if msg == "EXIT":
                                break

                            res = None
                            error: BaseException | None = None

                            try:
                                res = self._handle_message(msg)
                            except BaseException as exc:
                                error = exc

                            conn.send(
                                {
                                    "stdout": stdout.getvalue(),
                                    "stderr": stderr.getvalue(),
                                    "error": error,
                                    "result": res,
                                }
                            )

                        except EOFError:
                            ...

                stdout.truncate(0)
                stderr.truncate(0)

    def _handle_message(self, message: t.Any) -> t.Any:
        return self.app(message)
