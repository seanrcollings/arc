import pytest
from arc.types import SemVer

import arc

VERSIONS = [
    "1.0.0-alpha",
    "1.0.0-alpha.1",
    "1.0.0-alpha.beta",
    "1.0.0-beta",
    "1.0.0-beta.2",
    "1.0.0-beta.11",
    "1.0.0-rc.1",
    "1.0.0",
    "2.0.0",
    "2.1.0",
    "2.1.1",
]


def test_precedence():
    for idx, version in enumerate(VERSIONS):
        if idx != 0:
            assert SemVer.parse(version) > SemVer.parse(VERSIONS[idx - 1])

        assert SemVer.parse(version) == SemVer.parse(version)

        if idx < len(VERSIONS) - 1:
            assert SemVer.parse(version) < SemVer.parse(VERSIONS[idx + 1])


def test_bump_major():
    version = SemVer.parse("1.2.3")
    assert version.bump_major() == SemVer.parse("2.0.0")


def test_bump_minor():
    version = SemVer.parse("1.2.3")
    assert version.bump_minor() == SemVer.parse("1.3.0")


def test_bump_patch():
    version = SemVer.parse("1.2.3")
    assert version.bump_patch() == SemVer.parse("1.2.4")


@pytest.mark.parametrize("value", VERSIONS)
def test_usage(value):
    @arc.command
    def command(version: SemVer):
        return version

    assert command(value) == SemVer.parse(value)
