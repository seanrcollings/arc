import textwrap

from arc.present.ansi import Ansi


class TextWrapper(textwrap.TextWrapper):
    def wrap(self, text: str):
        old_width = self.width
        self.width = self.width + (len(text) - Ansi.len(text))
        wrapped = super().wrap(text)
        self.width = old_width
        return wrapped


def fill(
    text: str,
    width: int,
    initial_indent: str = "",
    subsequent_indent: str = "",
):
    wrapper = TextWrapper(
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        replace_whitespace=True,
        drop_whitespace=True,
    )

    return wrapper.fill(text)
