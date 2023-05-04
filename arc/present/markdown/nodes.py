from __future__ import annotations
import typing as t
import abc
from dataclasses import dataclass

from arc import color
from arc.present.ansi import colorize
from arc.present import wrap
from arc.present.joiner import Join

if t.TYPE_CHECKING:
    from arc.config import PresentConfig


class Node(abc.ABC):
    @abc.abstractmethod
    def fmt(self, config: PresentConfig) -> str:
        ...


class InlineNode(Node):
    ...


class BlockNode(Node):
    ...


@dataclass
class Document(BlockNode):
    children: list[BlockNode]

    def fmt(self, config: PresentConfig) -> str:
        return (
            Join.together(child.fmt(config) for child in self.children).strip("\n")
            + "\n"
        )


@dataclass
class Heading(BlockNode):
    content: InlineNode
    level: int

    def fmt(self, config: PresentConfig) -> str:
        return colorize(f"{self.content.fmt(config).upper()}", color.fx.BOLD) + "\n"


@dataclass
class Paragraph(BlockNode):
    children: list[InlineNode]

    def fmt(self, config: PresentConfig) -> str:
        content = Join.together(child.fmt(config) for child in self.children)
        content = wrap.fill(content, config.width, config.indent, config.indent)
        return f"{content}\n\n"


@dataclass
class List(BlockNode):
    elements: list[InlineNode]

    def fmt(self, config: PresentConfig) -> str:
        elements = (f"• {element.fmt(config)}" for element in self.elements)

        return (
            Join.with_newline(
                wrap.fill(
                    el, config.width, config.indent + "  ", config.indent + "    "
                )
                for el in elements
            )
            + "\n\n"
        )


@dataclass
class Unformatted(BlockNode):
    content: str

    def fmt(self, config: PresentConfig) -> str:
        return self.content + "\n\n"


@dataclass
class HorizontalRule(BlockNode):
    def fmt(self, config: PresentConfig) -> str:
        return "—" * config.width + "\n\n"


@dataclass
class Text(InlineNode):
    children: list[InlineNode]

    def fmt(self, config: PresentConfig) -> str:
        return Join.together(child.fmt(config) for child in self.children)


@dataclass
class Fragment(InlineNode):
    content: str

    def fmt(self, config: PresentConfig) -> str:
        return self.content


@dataclass
class Spacer(InlineNode):
    def fmt(self, config: PresentConfig) -> str:
        return " "


@dataclass
class Emphasis(InlineNode):
    text: InlineNode

    def fmt(self, config: PresentConfig) -> str:
        return colorize(self.text.fmt(config), color.fx.ITALIC)


@dataclass
class Strong(InlineNode):
    text: InlineNode

    def fmt(self, config: PresentConfig) -> str:
        return colorize(self.text.fmt(config), color.fx.BOLD)


@dataclass
class Strikethrough(InlineNode):
    text: InlineNode

    def fmt(self, config: PresentConfig) -> str:
        return colorize(self.text.fmt(config), color.fx.STRIKETHROUGH)


@dataclass
class Underline(InlineNode):
    text: InlineNode

    def fmt(self, config: PresentConfig) -> str:
        return colorize(self.text.fmt(config), color.fx.UNDERLINE)


@dataclass
class Link(InlineNode):
    text: InlineNode

    def fmt(self, config: PresentConfig) -> str:
        return colorize(self.text.fmt(config), config.color.accent, color.fx.UNDERLINE)


@dataclass
class Code(InlineNode):
    text: Fragment

    def fmt(self, config: PresentConfig) -> str:
        return colorize(self.text.fmt(config), color.bg.GREY, color.fg.WHITE)


@dataclass
class Colored(InlineNode):
    text: InlineNode
    color_name: str

    def fmt(self, config: PresentConfig) -> str:
        return colorize(self.text.fmt(config), self.color(config))

    def color(self, config: PresentConfig) -> str:
        return eval(
            f"{self.color_name}",
            {"fg": color.fg, "bg": color.bg, "color": config.color},
        )
