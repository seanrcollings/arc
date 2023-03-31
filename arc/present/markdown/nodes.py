import abc
from dataclasses import dataclass
import textwrap

from arc import color
from arc.present.ansi import Ansi, colorize
from arc.present import wrap
from arc.present.joiner import Join
from arc.present.markdown.config import MarkdownConfig


class Node(abc.ABC):
    @abc.abstractmethod
    def fmt(self, config: MarkdownConfig) -> str:
        ...


class InlineNode(Node):
    ...


class BlockNode(Node):
    ...


@dataclass
class Document(BlockNode):
    children: list[BlockNode]

    def __str__(self) -> str:
        return self.fmt(MarkdownConfig())

    def fmt(self, config: MarkdownConfig) -> str:
        return Join.together(child.fmt(config) for child in self.children)


@dataclass
class Heading(BlockNode):
    content: InlineNode
    level: int

    def fmt(self, config: MarkdownConfig) -> str:
        return colorize(f"{self.content.fmt(config).upper()}", color.fx.BOLD) + "\n"


@dataclass
class Paragraph(BlockNode):
    children: list[InlineNode]

    def fmt(self, config: MarkdownConfig) -> str:
        content = Join.together(child.fmt(config) for child in self.children)
        content = wrap.fill(content, config.width, config.indent, config.indent)
        return f"{content}\n\n"


@dataclass
class List(BlockNode):
    elements: list[InlineNode]

    def fmt(self, config: MarkdownConfig) -> str:
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

    def fmt(self, config: MarkdownConfig) -> str:
        return self.content + "\n\n"


@dataclass
class Text(InlineNode):
    children: list[InlineNode]

    def fmt(self, config: MarkdownConfig) -> str:
        return Join.together(child.fmt(config) for child in self.children)


@dataclass
class Fragment(InlineNode):
    content: str

    def fmt(self, config: MarkdownConfig) -> str:
        return self.content


@dataclass
class Spacer(InlineNode):
    def fmt(self, config: MarkdownConfig) -> str:
        return " "


@dataclass
class Emphasis(InlineNode):
    text: InlineNode

    def fmt(self, config: MarkdownConfig) -> str:
        return colorize(self.text.fmt(config), color.fx.ITALIC)


@dataclass
class Strong(InlineNode):
    text: InlineNode

    def fmt(self, config: MarkdownConfig) -> str:
        return colorize(self.text.fmt(config), color.fx.BOLD)


@dataclass
class Strikethrough(InlineNode):
    text: InlineNode

    def fmt(self, config: MarkdownConfig) -> str:
        return colorize(self.text.fmt(config), color.fx.STRIKETHROUGH)


@dataclass
class Underline(InlineNode):
    text: InlineNode

    def fmt(self, config: MarkdownConfig) -> str:
        return colorize(self.text.fmt(config), color.fx.UNDERLINE)


@dataclass
class Link(InlineNode):
    text: InlineNode

    def fmt(self, config: MarkdownConfig) -> str:
        return colorize(self.text.fmt(config), color.fg.BLUE, color.fx.UNDERLINE)


@dataclass
class Code(InlineNode):
    text: Fragment

    def fmt(self, config: MarkdownConfig) -> str:
        return colorize(self.text.fmt(config), color.bg.GREY, color.fg.WHITE)
