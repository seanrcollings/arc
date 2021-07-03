from typing import Optional
import textwrap


class CommandDoc:
    def __init__(self, doc: str = None):
        self.doc: Optional[str] = doc
        self.description: str = ""
        self.sections: dict[str, str] = {}

        if doc:
            self.doc = textwrap.dedent(doc)

            sections = self.doc.split("\n#")
            self.description = sections[0]

            for section in sections[1:]:
                lines = section.split("\n")
                self.sections[lines[0].strip()] = textwrap.dedent("\n".join(lines[1:]))
