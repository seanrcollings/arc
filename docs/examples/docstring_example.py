import arc


@arc.command
def command():
    """Description for the command. It may
    spread over multiple lines.

    Or even multiple paragraphs! Each section only ends
    when a new section header is detected.

    # Section 1
    Sections can have any content you want in them, all that matters
    is that the header matches the expected syntax.

    # Section 2
    arc will preserve paragraphs (two sequential newlines), but may rewrap
    single new lines. You can prevent this by adding \\b before a block of text.
    this tells arc to use the original text-wrapping.

    \b
    Like this!
    Second line
    Third line
    """


command()
