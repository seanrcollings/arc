from __future__ import annotations

import itertools
import typing as t

if t.TYPE_CHECKING:
    from arc.define import Command, Param

# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = (
                previous_row[j + 1] + 1
            )  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row  # type: ignore

    return previous_row[-1]


Suggestions = dict[str, list[str]]


def string_suggestions(
    source: t.Iterable[str], possibilities: t.Iterable[str], max_distance: int
) -> Suggestions:
    suggestions: dict[str, list[str]] = {}

    for string in source:
        suggestions[string] = [
            p for p in possibilities if levenshtein(string, p) <= max_distance
        ]

    return suggestions


def subcommand_suggestions(
    source: list[str], command: Command, distance: int
) -> Suggestions:
    return string_suggestions(
        source[0:1],
        itertools.chain(*[com.all_names for com in command.subcommands.values()]),
        distance,
    )


def param_suggestions(
    source: t.Iterable[str], params: t.Iterable[Param[t.Any]], distance: int
) -> Suggestions:
    return string_suggestions(
        source,
        itertools.chain(*[param.get_param_names() for param in params]),
        distance,
    )
