from dataclasses import dataclass


@dataclass
class MarkdownConfig:
    color: bool = True
    indent_len: int = 4
    indent_chars: str = " "
    width: int = 80

    @property
    def indent(self) -> str:
        return self.indent_chars * self.indent_len
