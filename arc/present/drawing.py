import typing as t


justify = {
    "left": "<",
    "center": "^",
    "right": ">",
}

Justification = t.Literal["left", "center", "right"]


class BorderCorners(t.TypedDict):
    top_left: str
    top_right: str
    bot_left: str
    bot_right: str


class BorderInstersect(t.TypedDict):
    cross: str
    vert_left: str
    vert_right: str
    hori_top: str
    hori_bot: str


class Border(t.TypedDict):
    horizontal: str
    vertical: str
    corner: BorderCorners
    intersect: BorderInstersect


BORDER_LIGHT: Border = {
    "horizontal": "─",
    "vertical": "│",
    "corner": {
        "top_left": "┌",
        "top_right": "┐",
        "bot_left": "└",
        "bot_right": "┘",
    },
    "intersect": {
        "cross": "┼",
        "vert_left": "├",
        "vert_right": "┤",
        "hori_top": "┬",
        "hori_bot": "┴",
    },
}

BORDER_LIGHT_ROUNDED: Border = {
    "horizontal": "─",
    "vertical": "│",
    "corner": {
        "top_left": "╭",
        "top_right": "╮",
        "bot_left": "╰",
        "bot_right": "╯",
    },
    "intersect": {
        "cross": "┼",
        "vert_left": "├",
        "vert_right": "┤",
        "hori_top": "┬",
        "hori_bot": "┴",
    },
}

BORDER_HEAVY: Border = {
    "horizontal": "━",
    "vertical": "┃",
    "corner": {
        "top_left": "┏",
        "top_right": "┓",
        "bot_left": "┗",
        "bot_right": "┛",
    },
    "intersect": {
        "cross": "╋",
        "vert_left": "┣",
        "vert_right": "┫",
        "hori_top": "┳",
        "hori_bot": "┻",
    },
}

BORDER_PIPE: Border = {
    "horizontal": "═",
    "vertical": "║",
    "corner": {
        "top_left": "╔",
        "top_right": "╗",
        "bot_left": "╚",
        "bot_right": "╝",
    },
    "intersect": {
        "cross": "╬",
        "vert_left": "╠",
        "vert_right": "╣",
        "hori_top": "╦",
        "hori_bot": "╩",
    },
}


borders = {
    "light": BORDER_LIGHT,
    "heavy": BORDER_HEAVY,
    "pipe": BORDER_PIPE,
    "rounded": BORDER_LIGHT_ROUNDED,
}
