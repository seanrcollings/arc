from typing import List
from dataclasses import dataclass
from arc._utils import decorate_text


@dataclass
class Token:
    """Data Container class. Each match made by the
        tokenizer will result in one of these being returned
    """

    type: str
    value: str


@dataclass
class OptionNode:
    """Matches to:
        option=value
        option=2
        option='value with spaces'
        option="value with spaces"
        option=value,with,commas
    """

    name: str
    value: str

    def __repr__(self):
        return f"{self.name}={self.value}"


@dataclass
class FlagNode:
    """Matches to:
        --flag
        --other_flag
    """

    name: str

    def __repr__(self):
        return self.name


@dataclass
class ScriptNode:
    """Matches to:
        name
        script
        thing
    Will match to any valid string,
    and as such it must be checked last
    in the tokenizer
    """

    name: str
    options: List[OptionNode]
    flags: List[FlagNode]

    def __repr__(self, level=0):
        tabs = "\t" * level
        string = (
            f"{decorate_text('SCRIPT', tcolor='33')}\n{tabs}"
            f"name: {decorate_text(self.name, tcolor='32')}"
            f"\n{tabs}options: {', '.join([decorate_text(str(o)) for o in self.options])}"
            f"\n{tabs}flags: {', '.join([decorate_text(str(f)) for f in self.flags])}"
        )
        return string


@dataclass
class UtilNode:
    """Matches to:
        util:
        name:
        thing:
    """

    name: str
    script: ScriptNode

    def __repr__(self):
        string = (
            f"{decorate_text('UTILITY', tcolor='33')}\n"
            f"name: {decorate_text(self.name, tcolor='32')}"
            f"\nscript: \n\t{self.script.__repr__(level=1)}"
        )
        return string
