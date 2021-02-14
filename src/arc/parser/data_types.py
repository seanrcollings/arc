from typing import List, Union, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from arc.color import fg, effects, bg
from arc.utils import symbol
from arc.formatters import Box


class TokenizerMode(Enum):
    COMMAND = symbol("command")
    BODY = symbol("body")


COMMAND = symbol("command")
FLAG = symbol("flags")
ARGUMENT = symbol("arguments")
POS_ARGUMENT = symbol("positional argument")
KEY_ARGUMENT = symbol("key argument")


@dataclass
class Token:
    """Data Container class. Each match made by the
    tokenizer will result in one of these being returned
    """

    type: symbol
    value: Union[Dict[str, str], str]


@dataclass
class ArgNode:
    name: Optional[str]
    value: str
    kind: symbol

    def __str__(self):
        if self.kind == KEY_ARGUMENT:
            return f"{self.name}={self.value}"
        if self.kind == POS_ARGUMENT:
            return str(self.value)
        if self.kind == FLAG:
            return f"--{self.name}"


@dataclass
class CommandNode:
    namespace: List[str]
    args: List[ArgNode]

    def __str__(self):
        color_map = {
            COMMAND: bg.GREEN,
            FLAG: bg.YELLOW,
            ARGUMENT: bg.BLUE,
            POS_ARGUMENT: bg.BLUE,
            KEY_ARGUMENT: bg.BLUE,
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

        return str(Box(f"{command} {args}\n\n{key}", justify="left"))

    def empty_namespace(self):
        return len(self.namespace) == 0
