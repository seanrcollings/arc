import contextlib
import typing as t
import logging
from io import StringIO
from multiprocessing import connection

from arc.runtime.serve.messages import InputRequest, InputResponse, Output

from arc.present import out


class NetworkOutput(StringIO):
    def __init__(
        self,
        conn: connection.Connection,
        stream: t.Literal["stdout", "stderr"],
        logger: logging.Logger,
    ) -> None:
        super().__init__()
        self.conn = conn
        self.stream = stream
        self.logger = logger

    def isatty(self) -> bool:
        return True

    def flush(self) -> None:
        self.logger.debug(f"Flushing {self.stream} over network")
        value = self.getvalue()

        if not value:
            self.logger.debug(f"Nothing to flush for {self.stream}")
            super().flush()
            return

        self.conn.send(Output(value, self.stream))
        self.truncate(0)
        self.seek(0)
        super().flush()


class NetworkInput(StringIO):
    def __init__(self, conn: connection.Connection, logger: logging.Logger) -> None:
        super().__init__()
        self.conn = conn
        self.logger = logger

    def read(self, size: int | None = -1) -> str:
        self.logger.debug("Reading from input over network")
        self.write("test\n")
        return super().read(size)

    def readline(self, size: int | None = -1) -> str:  # type: ignore
        self.logger.debug("Reading from input over network")
        self.conn.send(InputRequest())
        res = self.conn.recv()
        assert isinstance(res, InputResponse)
        return res.text


class redirect_stdin(contextlib._RedirectStream[NetworkInput]):
    _stream = "stdin"


@contextlib.contextmanager
def redirect_streams(
    conn: connection.Connection, logger: logging.Logger
) -> t.Iterator[tuple[NetworkOutput, NetworkOutput, NetworkInput]]:
    with (
        contextlib.redirect_stdout(NetworkOutput(conn, "stdout", logger)) as stdout,
        contextlib.redirect_stderr(NetworkOutput(conn, "stderr", logger)) as stderr,
        redirect_stdin(NetworkInput(conn, logger)) as stdin,
    ):
        console = out._default_console()
        console.default_print_stream = stdout
        console.default_log_stream = stderr

        try:
            yield stdout, stderr, stdin
        finally:
            stdout.flush()
            stderr.flush()
