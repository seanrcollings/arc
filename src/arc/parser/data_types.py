from typing import List, Union, Dict
from dataclasses import dataclass
from arc.color import fg, effects


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

    def __repr__(self):
        return f"{self.name}={self.value}"


@dataclass
class CommandNode:
    namespace: List[str]
    args: List[KeywordNode]

    def __repr__(self):
        return (
            f"{fg.GREEN}COMMAND{effects.CLEAR}\n"
            f"Namespace: {self.namespace}"
            f"Arguments: {self.args}"
        )
