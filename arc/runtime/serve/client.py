from __future__ import annotations
import typing as t
from multiprocessing import connection

from .messages import Message


class Client:
    def __init__(self, address: tuple[str, int]) -> None:
        self.conn = connection.Client(address)

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args: t.Any) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    def send(self, msg: Message) -> None:
        self.conn.send(msg)

    def recv(self) -> Message:
        return self.conn.recv()
