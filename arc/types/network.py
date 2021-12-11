import ipaddress
from urllib.parse import urlparse
import webbrowser
import typing as t

from arc.types.helpers import join_or, match, validate
from arc import errors

__all__ = ["IPAddress", "Url", "HttpUrl", "PostgresUrl", "stricturl"]

IPAddress = t.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


@validate
class Url(str):
    allowed_schemes: t.ClassVar[set[str]] = set()
    strip_whitespace: t.ClassVar[bool] = True
    host_required: t.ClassVar[bool] = False
    user_required: t.ClassVar[bool] = False
    matches: t.ClassVar[t.Optional[str]] = None

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

    def _validate_url(self):
        if self.allowed_schemes and self.scheme not in self.allowed_schemes:
            raise ValueError(f"scheme must be {join_or(tuple(self.allowed_schemes))}")

        if self.host_required and not self.host:
            raise ValueError("hostname required")

        if self.user_required and not self.username:
            raise ValueError("username required")

        if self.matches:
            if (err := match(self.matches, self)).err:
                raise ValueError(str(err))

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


def stricturl(
    allowed_schemes: set[str] = None,
    strip_whitespace: bool = True,
    host_required: bool = False,
    user_required: bool = False,
    matches: str = None,
) -> type[Url]:
    """Creates a custom `Url` type with specific validations

    Args:
        allowed_schemes (set[str], optional): The allowed url schemes
            (http, https, ftp, ssh, etc...). Defaults to None.
        strip_whitespace (bool, optional): Remove leading and trailing whitespace.
            Defaults to True.
        host_required (bool, optional): Require host portion of the URL (example.com).
            Defaults to True.
        user_required (bool, optional): Requires a username to be present in the URL
            (sean@example.com). Defaults to False.
        matches (str, optional): Regex string to match input against. Defaults to None.

    Returns:
        type[Url]: StrictUrl type
    """
    return type(
        "StrictUrl",
        (Url,),
        {
            "allowed_schemes": allowed_schemes,
            "strip_whitespace": strip_whitespace,
            "host_required": host_required,
            "user_required": user_required,
            "matches": matches,
        },
    )
