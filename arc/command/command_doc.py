import textwrap
from typing import Union
from arc.color import fg, effects


def header(text: str):
    return f"{effects.BOLD}{fg.WHITE.bright}{text.upper()}{effects.CLEAR}"


def section(heading: str, content: Union[str, list[str]]):
    if isinstance(content, list):
        content = textwrap.dedent("\n".join(content)).strip("\n")

    return header(heading) + "\n" + textwrap.indent(content, prefix="  ") + "\n\n"


class CommandDoc:

    DEFAULT_SECTION = "description"

    def __init__(self, doc: str = None, section_order: tuple = None):
        self.sections: dict[str, str] = {}
        self.order: tuple = section_order or tuple()
        if doc:
            self.parse_docstring(doc)

    def __str__(self):
        string = ""
        for key in self.order:
            string += section(key, self.sections[key].strip("\n"))

        for title, content in [
            (key, val) for key, val in self.sections.items() if key not in self.order
        ]:
            string += section(title, content.strip("\n"))

        return string.strip("\n")

    def parse_docstring(self, doc: str):
        """Parses a doc string into sections

        Sections are denoted by a new line, and
        then a line beginning with `#`. Whatever
        comes after the `#` will be the key in
        the sections dict. And all content between
        that `#` and the next `#` will be the value.

        The first section of the docstring is not
        required to possess a section header, and
        will be entered in as the `description` section.
        """
        lines = [line.strip() for line in doc.split("\n")]
        current_section = self.DEFAULT_SECTION

        for line in lines:
            if line.startswith("#"):
                current_section = line[1:].strip()
            elif line != "" or current_section != self.DEFAULT_SECTION:
                self.update_section(current_section, line + "\n")

    def add_section(self, title: str, content: str):
        """Adds a section with `title` and `content`"""
        self.sections[title] = content

    def update_section(self, key: str, to_add: str):
        """Updates a section. If that section
        does not exist, creates it"""
        key = key.lower().strip()
        if key in self.sections:
            self.sections[key] += to_add
        else:
            self.add_section(key, to_add)
