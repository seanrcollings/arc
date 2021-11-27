import pytest
from arc.types import network
from arc import CLI


class TestImpl:
    def test_parse(self):
        network.Url.parse(
            "https://google.com;params?key=val#fragment"
        ) == "https://google.com;params?key=val#fragment"

    def test_allowed_schemes(self):
        with pytest.raises(ValueError):
            network.HttpUrl.parse("scheme://google.com")
