from __future__ import annotations
import typing as t
from collections import deque
from arc.present.markdown.nodes import (
    BlockNode,
    Code,
    Document,
    Emphasis,
    Fragment,
    Heading,
    InlineNode,
    Link,
    List,
    Paragraph,
    Spacer,
    Strikethrough,
    Strong,
    Text,
    Underline,
    Unformatted,
    Colored,
)

if t.TYPE_CHECKING:
    from arc.config import PresentConfig


class InputDeque(deque[str]):
    def peek(self) -> str | None:
        if not self:
            return None

        return self[0]


class MarkdownParser:
    def parse(self, input: str) -> Document:
        stream = InputDeque(line for line in input.strip().split("\n"))

        nodes: list[BlockNode] = []

        while stream:
            curr = stream[0]

            if not curr:
                stream.popleft()
                continue

            if curr.startswith("#"):
                stream.popleft()
                nodes.append(self.parse_heading(curr))
            elif curr.startswith("-"):
                nodes.append(self.parse_list(stream))
            elif curr == "```":
                stream.popleft()
                nodes.append(self.parse_unformatted(stream))
            else:
                nodes.append(self.parse_paragraph(stream))

        return Document(nodes)

    def parse_heading(self, line: str) -> Heading:
        level = len(line) - len(line.lstrip("#"))
        line = line.rstrip("#")

        content = self.parse_inline(line[level:].strip())

        return Heading(content, level)

    def parse_paragraph(self, stream: deque[str]) -> Paragraph:
        lines: list[InlineNode] = []

        while stream and stream[0] != "":
            line = stream.popleft().strip()
            lines.append(self.parse_inline(line))
            lines.append(Spacer())

        if stream:
            stream.popleft()

        return Paragraph(lines)

    def parse_list(self, stream: InputDeque) -> List:
        elements: list[InlineNode] = []

        curr_element: str = stream.popleft()[1:].strip()

        while stream:
            line = stream.popleft()
            if not line:
                break

            if line.startswith("-"):
                elements.append(self.parse_inline(curr_element))
                curr_element = line[1:].strip()
            else:
                curr_element += " " + line.strip()

        elements.append(self.parse_inline(curr_element))
        return List(elements)

    def parse_unformatted(self, stream: InputDeque) -> Unformatted:
        lines: list[str] = []

        while stream and stream.peek() != "```":
            lines.append(stream.popleft())

        if stream:
            stream.popleft()

        return Unformatted("\n".join(lines))

    def parse_inline(self, content: str) -> InlineNode:
        stream = InputDeque(content)
        nodes: list[InlineNode] = []

        fragment = ""

        def new_fragment() -> None:
            nonlocal fragment
            nodes.append(Fragment(fragment))
            fragment = ""

        while stream:
            curr = stream.popleft()

            if curr == "*":
                new_fragment()
                if stream.peek() == "*":
                    stream.popleft()
                    nodes.append(self.parse_strong(stream))
                else:
                    nodes.append(self.parse_emphasis(stream))
            elif curr == "[":
                new_fragment()
                if stream.peek() == "[":
                    stream.popleft()
                    nodes.append(self.parse_colored(stream))
                else:
                    nodes.append(self.parse_link(stream))
            elif curr == "~":
                if stream.peek() == "~":
                    stream.popleft()
                    new_fragment()
                    nodes.append(self.parse_strikethrough(stream))
                else:
                    fragment += curr
            elif curr == "_":
                if stream.peek() == "_":
                    stream.popleft()
                    new_fragment()
                    nodes.append(self.parse_underline(stream))
                else:
                    fragment += curr
            elif curr == "`":
                new_fragment()
                nodes.append(self.parse_code(stream))
            else:
                fragment += curr

        if fragment:
            nodes.append(Fragment(fragment))

        return Text(nodes)

    def parse_emphasis(self, stream: deque[str]) -> Emphasis:
        return Emphasis(self.parse_inline_until(stream, "*"))

    def parse_strong(self, stream: deque[str]) -> Strong:
        return Strong(self.parse_inline_until(stream, "**"))

    def parse_code(self, stream: deque[str]) -> Code:
        return Code(Fragment(self.consume_until(stream, "`")))

    def parse_link(self, stream: deque[str]) -> Link:
        return Link(self.parse_inline_until(stream, "]"))

    def parse_strikethrough(self, stream: deque[str]) -> Strikethrough:
        return Strikethrough(self.parse_inline_until(stream, "~~"))

    def parse_underline(self, stream: deque[str]) -> Underline:
        return Underline(self.parse_inline_until(stream, "__"))

    def parse_colored(self, stream: deque[str]) -> Colored | InlineNode:
        color_name = self.consume_until(stream, "]]")

        # If we have a closing tag, but not opening tag, just return the text
        if color_name.startswith("/"):
            return Text([Fragment(f"[[{color_name}]]")])

        return Colored(
            self.parse_inline_until(stream, f"[[/{color_name}]]"), color_name
        )

    def parse_inline_until(self, stream: deque[str], string: str) -> InlineNode:
        text = self.consume_until(stream, string)
        return self.parse_inline(text)

    def consume_until(self, stream: deque[str], string: str) -> str:
        chars_length = len(string)
        text = ""

        while len(stream) >= chars_length and not all(
            stream[i] == string[i] for i in range(chars_length)
        ):
            text += stream.popleft()

        if stream:
            for _ in range(chars_length):
                if not stream:
                    break

                stream.popleft()

        return text


def markdown(text: str, config: PresentConfig) -> str:
    """Converts a markdown string to a formatted string."""
    parser = MarkdownParser()
    doc = parser.parse(text)
    return doc.fmt(config)
