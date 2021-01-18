from typing import List, Union
from dataclasses import dataclass
from arc.utils import decorate_text
from arc.color import fg


@dataclass
class Token:
    """Data Container class. Each match made by the
    tokenizer will result in one of these being returned
    """

    type: str
    value: str


@dataclass
class ArgNode:

    value: str

    def __repr__(self):
        return f"<ArgNode : {self.value}>"


@dataclass
class KeywordNode:
    name: str
    value: str

    def __repr__(self):
        return f"{self.name}={self.value}"


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
    args: List[Union[KeywordNode, ArgNode]]

    def __repr__(self, level=0):
        tabs = "\t" * level
        string = (
            f"{decorate_text('SCRIPT', tcolor=fg.YELLOW)}\n{tabs}"
            f"name: {decorate_text(self.name, tcolor=fg.YELLOW)}"
            f"\n{tabs}args: {', '.join([decorate_text(str(o)) for o in self.args])}"
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
            f"name: {decorate_text(self.name, tcolor=fg.GREEN)}\n"
            f"script: \n\t{self.script.__repr__(level=1)}"
        )
        return string
