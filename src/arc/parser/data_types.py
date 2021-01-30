from typing import List, Union, Dict, cast
from dataclasses import dataclass
from arc.color import fg, effects, bg

from arc import config


COMMAND = "command"
FLAG = "flag"
ARGUMENT = "argument"


@dataclass
class Token:
    """Data Container class. Each match made by the
    tokenizer will result in one of these being returned
    """

    type: str
    value: Union[Dict[str, str], str]


@dataclass
class ArgNode:

    value: str

    def __repr__(self):
        return f"<ArgNode : {self.value}>"


@dataclass
class KeywordNode:
    name: str
    value: str
    kind: str

    def __str__(self):
        if self.kind == ARGUMENT:
            return f"{self.name}={self.value}"
        return f"--{self.name}"


@dataclass
class CommandNode:
    namespace: List[str]
    args: List[KeywordNode]

    def __str__(self):
        color_map = {
            COMMAND: bg.GREEN,
            FLAG: bg.YELLOW,
            ARGUMENT: bg.BLUE,
        }

        command = (
            f"{fg.BLACK.bright}{color_map[COMMAND]}"
            f" {':'.join(self.namespace)} {effects.CLEAR}"
        )

        args = " ".join(
            f"{fg.BLACK.bright}{color_map[arg.kind]}" f" {arg} {effects.CLEAR}"
            for arg in self.args
        )

        key = (
            f"COMMAND: {color_map[COMMAND]}  {effects.CLEAR} "
            f"ARGUMENT: {color_map[ARGUMENT]}  {effects.CLEAR}"
            f" FLAG: {color_map[FLAG]}  {effects.CLEAR} "
        )

        return f"{command} {args}\n\n{key}"
