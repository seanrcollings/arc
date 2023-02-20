import typing as t

K = t.TypeVar("K")
V = t.TypeVar("V")


class AliasDict(dict[K, V]):
    """Dict subclass for storing aliases to keys alongside the actual key"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.aliases: dict[K, K] = {}
        """Maps aliases to the cannonical key"""

    def get(self, key: K, default=None):
        """Wraps `dict.get()` but also checks for aliases"""
        if super().__contains__(key):
            return self[key]
        if key in self.aliases:
            return self[self.aliases[key]]

        return default

    def __contains__(self, key: object):
        return super().__contains__(key) or key in self.aliases

    def add_alias(self, key: K, alias: K):
        """Add an `alias` for `key`"""
        self.aliases[alias] = key

    def add_aliases(self, key: K, *aliases: K):
        """Add an several `aliass` for `key`"""
        for alias in aliases:
            self.add_alias(key, alias)

    def aliases_for(self, key: K) -> list[K]:
        return [alias for alias, val in self.aliases.items() if val == key]
