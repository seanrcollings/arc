from __future__ import annotations
import re
import typing as t
from arc import errors

SEMVAR_REGEX = re.compile(
    r"(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)"
    r"+(?P<prerelease>-[0-9A-Za-z-.]+)?"
    r"(?P<build>\+[0-9A-Za-z-.]+)?"
)


class SemVar:
    """Represents a semantically versioned string.
    Reference: https://semver.org/spec/v2.0.0.html
    """

    _prerelease_prefix = "-"
    _build_prefix = "+"
    _metadata_sep = "."

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: t.Optional[str] = None,
        build: t.Optional[str] = None,
    ):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = (
            tuple(prerelease.split(self._metadata_sep)) if prerelease else tuple()
        )
        self.build = tuple(build.split(self._metadata_sep)) if build else tuple()

    def __str__(self):
        string = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            string += (
                f"{self._prerelease_prefix}{self._metadata_sep.join(self.prerelease)}"
            )
        if self.build:
            string += f"{self._build_prefix}{self._metadata_sep.join(self.build)}"

        return string

    def __repr__(self):
        return f"SemVar('{self}')"

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other) -> bool:
        if self.version == other.version:
            # Version with prelease info has a lower
            # precedence than one without
            # 1.0.0-alpha < 1.0.0
            if self.prerelease and not other.prerelease:
                return True
            elif not self.prerelease and other.prerelease:
                return False

            results = []
            for pair in zip(self.prerelease, other.prerelease):
                if all(i.isnumeric() for i in pair):
                    results.append(
                        int(pair[0]) < int(pair[1]) or int(pair[0]) == int(pair[1])
                    )
                else:
                    results.append(pair[0] < pair[1] or pair[0] == pair[1])

            return any(results)
        else:
            return self.version < other.version

    def __le__(self, other) -> bool:
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other) -> bool:
        return not self.__lt__(other) and not self.__eq__(other)

    def __ge__(self, other) -> bool:
        return self.__eq__(other) or self.__gt__(other)

    @property
    def version(self):
        return (self.major, self.minor, self.patch)

    @classmethod
    def parse(cls, string: str):
        match = SEMVAR_REGEX.match(string)
        if not match:
            raise ValueError("Invalid semantic version string")

        groups = match.groupdict()
        if groups["prerelease"]:
            groups["prerelease"] = groups["prerelease"].strip(cls._prerelease_prefix)

        if groups["build"]:
            groups["build"] = groups["build"].strip(cls._prerelease_prefix)

        return cls(
            major=int(groups["major"]),
            minor=int(groups["minor"]),
            patch=int(groups["patch"]),
            prerelease=groups["prerelease"],
            build=groups["build"],
        )

    @classmethod
    def __convert__(cls, value: str):
        try:
            return cls.parse(value)
        except ValueError as e:
            raise errors.ConversionError(
                value, "invalid semantic version string"
            ) from e
