import pytest
import ipaddress

from arc.types import network
from arc import CLI

IPV4 = [
    "0.0.0.0",
    "1.1.1.1",
    "10.10.10.10",
    "192.168.0.1",
    "255.255.255.255",
    0,
    16_843_009,
    168_430_090,
    3_232_235_521,
    4_294_967_295,
]

IPV6 = [
    "::1:0:1",
    "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",
    4_294_967_297,
    340_282_366_920_938_463_463_374_607_431_768_211_455,
]


class TestAddresses:
    @pytest.mark.parametrize("value", IPV4)
    def test_ipv4_success(self, cli: CLI, value):
        @cli.command()
        def ipv4(address: ipaddress.IPv4Address):
            return address

        assert cli(f"ipv4 {value}") == ipaddress.IPv4Address(value)

    @pytest.mark.parametrize("value", IPV6)
    def test_ipv6(self, cli: CLI, value):
        @cli.command()
        def ipv6(address: ipaddress.IPv6Address):
            return address

        assert cli(f"ipv6 {value}") == ipaddress.IPv6Address(value)

    @pytest.mark.parametrize(
        "value,cls",
        [(ip, ipaddress.IPv4Address) for ip in IPV4]
        + [(ip, ipaddress.IPv6Address) for ip in IPV6],  # type: ignore
    )
    def test_ip(self, cli: CLI, value, cls):
        @cli.command()
        def ip(address: network.IPAddress):
            return address

        assert cli(f"ip {value}") == cls(value)


# From: https://github.com/samuelcolvin/pydantic/blob/master/tests/test_networks.py
URLS = [
    "http://example.org",
    "http://test",
    "http://localhost",
    "https://example.org/whatever/next/",
    "postgres://user:pass@localhost:5432/app",
    "postgres://just-user@localhost:5432/app",
    "postgresql+asyncpg://user:pass@localhost:5432/app",
    "postgresql+pg8000://user:pass@localhost:5432/app",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/hatch",
    "postgresql+psycopg2cffi://user:pass@localhost:5432/app",
    "postgresql+py-postgresql://user:pass@localhost:5432/app",
    "postgresql+pygresql://user:pass@localhost:5432/app",
    "foo-bar://example.org",
    "foo.bar://example.org",
    "foo0bar://example.org",
    "https://example.org",
    "http://localhost",
    "http://localhost/",
    "http://localhost:8000",
    "http://localhost:8000/",
    "https://foo_bar.example.com/",
    "ftp://example.org",
    "ftps://example.org",
    "http://example.co.jp",
    "http://www.example.com/a%C2%B1b",
    "http://www.example.com/~username/",
    "http://info.example.com?fred",
    "http://info.example.com/?fred",
    "http://xn--mgbh0fb.xn--kgbechtv/",
    "http://example.com/blue/red%3Fand+green",
    "http://www.example.com/?array%5Bkey%5D=value",
    "http://xn--rsum-bpad.example.org/",
    "http://123.45.67.8/",
    "http://123.45.67.8:8329/",
    "http://[2001:db8::ff00:42]:8329",
    "http://[2001::1]:8329",
    "http://[2001:db8::1]/",
    "http://www.example.com:8000/foo",
    "http://www.cwi.nl:80/%7Eguido/Python.html",
    "https://www.python.org/путь",
    "http://андрей@example.com",
    "https://exam_ple.com/",
    "http://twitter.com/@handle/",
    "http://11.11.11.11.example.com/action",
    "http://abc.11.11.11.11.example.com/action",
    "http://example#",
    "http://example/#",
    "http://example/#fragment",
    "http://example/?#",
    "http://example.org/path#",
    "http://example.org/path#fragment",
    "http://example.org/path?query#",
    "http://example.org/path?query#fragment",
    "file://localhost/foo/bar",
]

HTTP_URLS = (url for url in URLS if url.startswith("http"))

POSTGRES_URLS = (url for url in URLS if url.startswith("postgres"))


class TestUrl:
    @pytest.mark.parametrize("value", URLS)
    def test_parse(self, value):
        assert network.Url.parse(value) == value

    class TestValidators:
        def test_allowed_schemes(self):
            assert network.HttpUrl.parse("http://example.com") == "http://example.com"
            assert network.HttpUrl.parse("https://example.com") == "https://example.com"

            with pytest.raises(ValueError):
                network.HttpUrl.parse("scheme://example.com")

        def test_strip_whitespace(self):
            assert (
                network.Url.parse("    https://example.com    ")
                == "https://example.com"
            )

            NoStrip = network.stricturl(strip_whitespace=False)
            assert (
                NoStrip.parse("    https://example.com    ")
                == "    https://example.com    "
            )

        def test_user_required(self):
            UserRequired = network.stricturl(user_required=True)
            assert (
                UserRequired.parse("https://name@example.com")
                == "https://name@example.com"
            )

            with pytest.raises(ValueError):
                UserRequired.parse("https://example.com")

        def test_host_required(self):
            HostRequired = network.stricturl(host_required=True)
            assert HostRequired.parse("https://example.com") == "https://example.com"

            with pytest.raises(ValueError):
                HostRequired.parse("path/path")

    class TestUsage:
        @pytest.mark.parametrize("value", URLS)
        def test_url(self, cli: CLI, value):
            @cli.command()
            def url(url: network.Url):
                return url

            assert cli(f"url {value}") == value

        @pytest.mark.parametrize("value", HTTP_URLS)
        def test_http_url(self, cli: CLI, value):
            @cli.command()
            def url(url: network.HttpUrl):
                return url

            assert cli(f"url {value}") == value

        @pytest.mark.parametrize("value", POSTGRES_URLS)
        def test_psql_url(self, cli: CLI, value):
            @cli.command()
            def url(url: network.PostgresUrl):
                return url

            assert cli(f"url {value}") == value
