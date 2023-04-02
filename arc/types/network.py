from __future__ import annotations

import ipaddress
import typing as t
from urllib.parse import urlparse

from arc import errors
from arc.present.joiner import Join

__all__ = [
    "IPAddress",
    "Url",
    "HttpUrl",
    "PostgresUrl",
    "WebSocketUrl",
    "FtpUrl",
    "MysqlUrl",
]

IPAddress = t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


class AllowedUrlProtocols:
    def __init__(self, *allowed: str) -> None:
        self.allowed_protocols = set(allowed)

    def __call__(self, value: Url) -> Url:
        if value.protocol not in self.allowed_protocols:
            raise errors.ValidationError(
                f"protocol must be {Join.with_or(tuple(self.allowed_protocols))}"
            )

        return value


class RequiredUrlComponents:
    def __init__(self, *components: str) -> None:
        self.components = components

    def __call__(self, value: Url) -> Url:
        for comp in self.components:
            if getattr(value, comp) is None:
                raise errors.ValidationError(f"{comp} is required in URL")

        return value


class Url(str):
    __slots__ = (
        "url",
        "protocol",
        "netloc",
        "username",
        "password",
        "host",
        "port",
        "path",
        "params",
        "query",
        "fragment",
    )

    def __new__(cls, url: str, **_kwargs: t.Any) -> Url:
        return super().__new__(cls, url)

    def __init__(
        self,
        url: str,
        *,
        protocol: str | None = None,
        netloc: str | None = None,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: t.Optional[int] = None,
        path: str | None = None,
        params: str | None = None,
        query: str | None = None,
        fragment: str | None = None,
    ):
        super().__init__()
        self.url = url
        self.protocol = protocol
        self.netloc = netloc
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.path = path
        self.params = params
        self.query = query
        self.fragment = fragment

    @classmethod
    def parse(cls, url: str) -> Url:

        url = url.strip()

        result = urlparse(url.strip())

        parsed: Url = cls(
            url=url,
            protocol=result.scheme,
            netloc=result.netloc,
            username=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port,
            path=result.path,
            params=result.params,
            query=result.query,
            fragment=result.fragment,
        )

        return parsed

    @classmethod
    def __convert__(cls, value: str) -> Url:
        try:
            return cls.parse(value)
        except ValueError as e:
            raise errors.ConversionError(value, str(e)) from e


HttpUrl = t.Annotated[Url, AllowedUrlProtocols("http", "https")]
WebSocketUrl = t.Annotated[Url, AllowedUrlProtocols("wss")]
FtpUrl = t.Annotated[Url, AllowedUrlProtocols("ftp")]
MysqlUrl = t.Annotated[Url, AllowedUrlProtocols("mysql")]
PostgresUrl = t.Annotated[
    Url,
    AllowedUrlProtocols(
        "postgresql",
        "postgres",
        "postgresql+asyncpg",
        "postgresql+pg8000",
        "postgresql+psycopg2",
        "postgresql+psycopg2cffi",
        "postgresql+py-postgresql",
        "postgresql+pygresql",
    ),
]
