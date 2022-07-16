from __future__ import annotations
import ipaddress
from urllib.parse import urlparse
import webbrowser
import typing as t

from arc import errors
from arc.present.helpers import Joiner

__all__ = ["IPAddress", "Url", "HttpUrl", "PostgresUrl"]

IPAddress = t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


class Url(str):
    allowed_schemes: t.ClassVar[set[str]] = set()
    strip_whitespace: t.ClassVar[bool] = True
    host_required: t.ClassVar[bool] = False
    user_required: t.ClassVar[bool] = False

    __slots__ = (
        "url",
        "scheme",
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

    def __new__(cls, url: str, **_kwargs):
        return super().__new__(cls, url)

    def __init__(
        self,
        url: str,
        *,
        scheme: str | None = None,
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
        self.scheme = scheme
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
    def parse(cls, url: str):

        if cls.strip_whitespace:
            url = url.strip()

        result = urlparse(url.strip())

        parsed: Url = cls(
            url=url,
            scheme=result.scheme,
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

        parsed._validate()
        return parsed

    def _validate(self):
        if self.allowed_schemes and self.scheme not in self.allowed_schemes:
            raise ValueError(
                f"scheme must be {Joiner.with_or(tuple(self.allowed_schemes))}"
            )

        if self.host_required and not self.host:
            raise ValueError("hostname required")

        if self.user_required and not self.username:
            raise ValueError("username required")

    @classmethod
    def __convert__(cls, value):
        try:
            return cls.parse(value)
        except ValueError as e:
            raise errors.ConversionError(value, str(e)) from e


class HttpUrl(Url):
    allowed_schemes = {"http", "https"}

    def open(self):
        """Opens the url in the user's web browser"""
        webbrowser.open_new_tab(self)


class PostgresUrl(Url):
    allowed_schemes = {
        "postgresql",
        "postgres",
        "postgresql+asyncpg",
        "postgresql+pg8000",
        "postgresql+psycopg2",
        "postgresql+psycopg2cffi",
        "postgresql+py-postgresql",
        "postgresql+pygresql",
    }
