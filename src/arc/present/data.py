from typing import Union, Literal

justifications = {
    "left": "<",
    "center": "^",
    "right": ">",
}

Justification = Union[Literal["left"], Literal["center"], Literal["right"]]
