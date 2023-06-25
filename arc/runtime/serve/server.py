from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import typing as t
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from multiprocessing import connection

from arc import errors
from arc.present import out
from arc.logging import logger
from .messages import (
    Close,
    Output,
    CommandResult,
    Message,
    Ping,
    Pong,
    Text,
    Exit,
    RunCommand,
    Error,
)

if t.TYPE_CHECKING:
    from arc.runtime.app import App


class NetworkIO(StringIO):
    def __init__(
        self, conn: connection.Connection, stream: t.Literal["stdout", "stderr"]
    ) -> None:
        super().__init__()
        self.conn = conn
        self.stream = stream

    def isatty(self) -> bool:
        return True

    def flush(self) -> None:
        logger.debug(f"Flushing {self.stream} over network")
        value = self.getvalue()

        if not value:
            logger.debug(f"Nothing to flush for {self.stream}")
            super().flush()
            return

        self.conn.send(Output(value, self.stream))
        self.truncate(0)
        self.seek(0)
        super().flush()


class Server:
    listener: connection.Listener | None = None

    def __init__(self, app: App, address: tuple[str, int], workers: int = 8) -> None:
        self.app = app
        self.address = address
        self.workers = workers
        self._running = False

    def __enter__(self) -> Server:
        self.listener = connection.Listener(self.address)
        self.listener._listener._socket.settimeout(1)  # type: ignore
        return self

    def __exit__(self, *args: t.Any) -> None:
        assert self.listener is not None
        self.listener.close()

    def serve(self) -> None:
        assert self.listener is not None

        self._running = True

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            while self._running:
                try:
                    conn = self.listener.accept()
                    executor.submit(self.handle_connection, conn)
                except TimeoutError:
                    # TODO: Is there a better way to do this?
                    ...

    def handle_connection(self, conn: connection.Connection) -> None:
        self.app.logger.info(f"Server got connection from {conn.fileno()}")

        with conn:
            while True:
                if conn.poll():
                    msg: Message = conn.recv()
                    try:
                        should_close = self.handle_message(conn, msg)
                    except Exception as exc:
                        self.app.logger.exception(exc)
                        conn.send(Error(str(exc)))
                        should_close = True

                    if should_close:
                        break

        self.app.logger.info(f"Closing connection {conn.fileno()}")

    def handle_message(self, conn: connection.Connection, msg: Message) -> bool:
        self.app.logger.info(f"Processing message: {msg}")

        match msg:
            case Ping():
                conn.send(Pong())
            case Text(text):
                conn.send(Text(f"Message recieved: {text}"))
            case Exit():
                self._running = False
                self.app.logger.info("Exiting")
            case Close():
                return True
            case RunCommand(command):
                self.app.logger.info(f"Running command: {command}")
                res = self.run_command(conn, command)
                conn.send(CommandResult(res))
            case _:
                self.app.logger.info(f"Unknown message type: {msg}")

        return False

    def run_command(self, conn: connection.Connection, command: str) -> t.Any:
        with (
            redirect_stdout(NetworkIO(conn, "stdout")) as stdout,
            redirect_stderr(NetworkIO(conn, "stderr")) as stderr,
        ):
            console = out._default_console()
            console.default_print_stream = stdout
            console.default_log_stream = stderr

            try:
                return self.app(
                    command, ctx={"arc.serve.conn": conn, "arc.serve": True}
                )
            except errors.ArcError as exc:
                return str(exc)
            except errors.Exit as exc:
                return f"Exited with code: {exc.code}"
            finally:
                stdout.flush()
                stderr.flush()
