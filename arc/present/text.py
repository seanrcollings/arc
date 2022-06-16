from __future__ import annotations
import itertools
import typing as t
from arc.color import colorize, effects


class Span:
    def __init__(self, string: str, *effects: str):
        self.string = string
        self.effects = effects

    def __len__(self):
        return len(self.string)

    def plain(self, spec: str):
        return format(self.string, spec)

    def colored(self, spec: str):
        return colorize(format(self.string, spec), *self.effects)


class Text:
    def __init__(self, *spans: Span):
        self.spans = spans

    def __len__(self):
        return sum(len(span) for span in self.spans)

    def __add__(self, other: Span):
        if isinstance(other, Span):
            return Text(*self.spans, other)

        return NotImplemented

    def __or__(self, other: Text):
        if isinstance(other, Text):
            return Text(*(self.spans + other.spans))

        return NotImplemented

    def __format__(self, spec: str) -> str:
        spec = spec or "plain"
        specs = spec.split("|")
        color_spec = specs[0]
        string_specs = specs[1].split(",") if len(specs) > 1 else []

        return "".join(
            getattr(span, color_spec)(spec)
            if isinstance(span, Span)
            else format(span, spec)
            for span, spec in itertools.zip_longest(
                self.spans, string_specs, fillvalue=""
            )
        )
