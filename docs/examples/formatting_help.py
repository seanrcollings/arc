import arc


@arc.command
def command():
    """**Command description**. Any text before the first section heading
        will be considered the command description.

    # Section Heading
    You can add a section heading to your help text by using a
    line that starts with a hash followed by a space. Any sections you
    define will be included in the help text below the auto-generated
    sections.

    Paragraphs are separated by blank lines. `arc` will handle wrapping the
    text for pargraphs automatically.

    # Lists
    You can create lists by using the following syntax:

    - This is a list item
    - This is another list item
    - This is a third list item

    # Unformatted text
    You can add unformatted text by surrounding the
    text with three backticks

    ```
        arc will not perform any formatting of this text.
            This lets you fully control how the text is displayed (Like tabbing it in!)
    ```

    `arc` actually takes advantage of this fact
    to have more more control over how the
    Argument and Options are displayed in the help text.
    """


command()
