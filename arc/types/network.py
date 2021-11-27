import ipaddress
from urllib.parse import urlparse, ParseResult
import webbrowser
import typing as t

from arc.types.helpers import join_or
from arc import errors

__all__ = ["IPAddress", "Url", "HttpUrl", "PostgresUrl", "stricturl"]

IPAddress = t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


class Url(str):
    allowed_schemes: t.ClassVar[set[str]] = set()
    strip_whitespace: t.ClassVar[bool] = True
    host_required: t.ClassVar[bool] = True
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
        return str.__new__(cls, url)

    def __init__(
        self,
        url: str,
        *,
        scheme: t.Optional[str] = None,
        netloc: t.Optional[str] = None,
        username: t.Optional[str] = None,
        password: t.Optional[str] = None,
        host: t.Optional[str] = None,
        port: t.Optional[int] = None,
        path: t.Optional[str] = None,
        params: t.Optional[str] = None,
        query: t.Optional[str] = None,
        fragment: t.Optional[str] = None,
    ):
        str.__init__(url)
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

        result = urlparse(url)
        cls.__validate_result(result)

        return cls(
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

    @classmethod
    def __validate_result(cls, result: ParseResult):
        if cls.allowed_schemes and result.scheme not in cls.allowed_schemes:
            raise ValueError(f"scheme must be {join_or(tuple(cls.allowed_schemes))}")

        if cls.host_required and not result.hostname:
            raise ValueError("hostname required")

        if cls.user_required and not result.username:
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
    allowed_schemes = {"postgresql", "postgres"}


def stricturl(allowed_schemes: set[str] = None) -> type[Url]:
    return type("StrictUrl", (Url,), {"allowed_schemes": allowed_schemes})
