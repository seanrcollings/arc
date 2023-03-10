from typing import Literal, Union

justifications = {
    "left": "<",
    "center": "^",
    "right": ">",
}

Justification = Union[Literal["left"], Literal["center"], Literal["right"]]
