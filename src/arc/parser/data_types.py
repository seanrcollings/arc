from typing import List
from dataclasses import dataclass
from arc.color import fg, bg, effects


def decorate_text(text: str, tcolor=fg.WHITE):
    return f"{tcolor}{text}{effects.CLEAR}"


@dataclass
class Token:
    """Data Container class. Each match made by the
    tokenizer will result in one of these being returned
    """

    type: str
    value: str


@dataclass
class ArgNode:
    """Matches to anything that isn't a flag or value"""

    value: str

    def __repr__(self):
        return f"<ArgNode : {self.value}>"


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
        return f"--{self.name}"


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
    args: List[ArgNode]

    def __repr__(self, level=0):
        tabs = "\t" * level
        string = (
            f"{decorate_text('SCRIPT', tcolor=fg.YELLOW)}\n{tabs}"
            f"name: {decorate_text(self.name, tcolor=fg.YELLOW)}"
            f"\n{tabs}options: {', '.join([decorate_text(str(o)) for o in self.options])}"
            f"\n{tabs}flags: {', '.join([decorate_text(str(f)) for f in self.flags])}"
            f"\n{tabs}other args: {', '.join([decorate_text(str(a)) for a in self.args])}"
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
            f"{decorate_text('UTILITY', tcolor=fg.YELLOW)}\n"
            f"name: {decorate_text(self.name, tcolor=bg.GREEN)}\n"
            f"\nscript: \n\t{self.script.__repr__(level=1)}"
        )
        return string
