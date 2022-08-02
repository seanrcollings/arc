from __future__ import annotations
import re
import typing as t
from arc import errors, typing as at
from arc.utils import cmp


# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEMVAR_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


# Partialy inspired by: https://github.com/python-semver/python-semver
class SemVer:
    """Read-only representation a semantically versioned string.
    Reference: https://semver.org/spec/v2.0.0.html
    """

    _prerelease_prefix = "-"
    _build_prefix = "+"
    _metadata_sep = "."

    def __init__(
        self,
        major: int = 0,
        minor: int = 0,
        patch: int = 0,
        prerelease: t.Optional[str] = None,
        build: t.Optional[str] = None,
    ):
        self._major: int = major
        self._minor: int = minor
        self._patch: int = patch
        self._prerelease: tuple[str, ...] = (
            tuple(prerelease.split(self._metadata_sep)) if prerelease else tuple()
        )
        self._build: tuple[str, ...] = (
            tuple(build.split(self._metadata_sep)) if build else tuple()
        )

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
        return f"SemVer({str(self)!r})"

    def __iter__(self):
        yield from (a for a in self.tuple() if a)

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def patch(self):
        return self._patch

    @property
    def prerelease(self):
        return self._prerelease

    @property
    def build(self):
        return self._build

    # Comparison Operators --------------------------------------------------------------------

    def compare(self, other: object) -> at.CompareReturn:
        """Compares `self` with `other`

        Args:
            other (SemVer): the second version for comparison

        Returns:
            at.CompareReturn: is negative if self < other,
             zero if self == other and strictly positive if self > other
        """

        if not isinstance(other, SemVer):
            return NotImplemented

        tup1, tup2 = self.tuple(), other.tuple()

        # Their version numbers are different,
        # no need to check the prerelease data
        comp = cmp(tup1[:3], tup2[:3])
        if comp:
            return comp

        # Their version numbers are the same
        # and we need to compare the prerelease data
        pr1, pr2 = self.prerelease, other.prerelease

        # No prerelease data for one or both versions
        if not comp and not pr1 and not pr2:
            return comp
        elif not pr1:
            return 1
        elif not pr2:
            return -1

        pr1 = tuple(int(p) if p.isnumeric() else p for p in pr1)  # type: ignore
        pr2 = tuple(int(p) if p.isnumeric() else p for p in pr2)  # type: ignore

        for part1, part2 in zip(pr1, pr2):
            comp = self._cmp_prerelease_tag(part1, part2)
            if comp:
                return comp

        return cmp(len(pr1), len(pr2))

    def _cmp_prerelease_tag(
        self, a: t.Union[str, int], b: t.Union[str, int]
    ) -> at.CompareReturn:
        """Compares two prerelease tags given the following conditions:
        - Identifiers consisting of only digits are compared numerically.
        - Identifiers with letters or hyphens are compared lexically in ASCII sort order.
        - Numeric identifiers always have lower precedence than non-numeric identifiers.
        """
        # Compared numerically
        if isinstance(a, int) and isinstance(b, int):
            return cmp(a, b)
        # Numeric identifiers have lower priority
        elif isinstance(a, int):
            return -1
        elif isinstance(b, int):
            return 1

        # Compared lexically
        return cmp(a, b)

    def __eq__(self, other) -> bool:
        return self.compare(other) == 0

    def __ne__(self, other) -> bool:
        return self.compare(other) != 0

    def __lt__(self, other) -> bool:
        return self.compare(other) == -1

    def __le__(self, other) -> bool:
        return self.compare(other) <= 0

    def __gt__(self, other) -> bool:
        return self.compare(other) == 1

    def __ge__(self, other) -> bool:
        return self.compare(other) >= 0

    # Utility Functions -----------------------------------------------------------------------

    def tuple(self):
        return (self.major, self.minor, self.patch, self.prerelease, self.build)

    def dict(self):
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "prerelease": self.prerelease,
            "build": self.build,
        }

    def bump_major(self):
        cls = type(self)
        return cls(self.major + 1)

    def bump_minor(self):
        cls = type(self)
        return cls(self.major, self.minor + 1)

    def bump_patch(self):
        cls = type(self)
        return cls(self.major, self.minor, self.patch + 1)

    # Conversion Utilities --------------------------------------------------------------------

    @classmethod
    def parse(cls, string: str):
        match = SEMVAR_REGEX.match(string)
        if not match:
            raise ValueError("Invalid semantic version string")

        groups = match.groupdict()

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
            raise errors.ConversionError(value, str(e)) from e
