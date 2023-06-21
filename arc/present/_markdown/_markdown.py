from __future__ import annotations
import typing as t
from arc.present._markdown.markdown_parser import MarkdownParser
from arc.present._markdown.nodes import Document

if t.TYPE_CHECKING:
    from arc.config import PresentConfig


def markdown(text: str, config: PresentConfig | None = None) -> str:
    """Converts a markdown string to a formatted string with the given config."""
    doc = parse_markdown(text)

    if config is None:
        from arc.config import PresentConfig

        config = PresentConfig()

    return doc.fmt(config)


def parse_markdown(text: str) -> Document:
    """Converts a markdown string to a formatted string."""
    parser = MarkdownParser()
    doc = parser.parse(text)
    return doc
