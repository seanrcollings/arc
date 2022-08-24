import typing as t


class MissingType:
    def __str__(self):
        return "MISSING"

    def __repr__(self):
        return "MISSING"


MISSING = MissingType()


NO_CONVERT = {None, bool, t.Any, MISSING}

COLLECTION_TYPES = (list, set, tuple)
