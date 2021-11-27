import pytest
from arc.types import SemVar

from arc import CLI, errors


class TestImpl:
    def test_version_precedence(self):
        assert SemVar.parse("1.0.0") == SemVar.parse("1.0.0")

        assert (
            SemVar.parse("1.0.0")
            < SemVar.parse("2.0.0")
            < SemVar.parse("2.1.0")
            < SemVar.parse("2.1.1")
        )

    def test_prerelease_precedence(self):
        assert SemVar.parse("1.0.0-alpha") == SemVar.parse("1.0.0-alpha")
        assert SemVar.parse("1.0.0-alpha") < SemVar.parse("1.0.0")

        assert (
            SemVar.parse("1.0.0-alpha")
            < SemVar.parse("1.0.0-alpha.1")
            < SemVar.parse("1.0.0-alpha.beta")
            < SemVar.parse("1.0.0-beta")
            < SemVar.parse("1.0.0-beta.2")
            < SemVar.parse("1.0.0-beta.11")
            < SemVar.parse("1.0.0-rc.1")
            < SemVar.parse("1.0.0")
        )


def test_usage(cli: CLI):
    @cli.command()
    def v(version: SemVar):
        return version

    assert cli("v 1.2.3") == SemVar.parse("1.2.3")
    assert cli("v 1.2.3-alpha+build") == SemVar.parse("1.2.3-alpha+build")

    with pytest.raises(errors.InvalidParamaterError):
        cli("v blah")