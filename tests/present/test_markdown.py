import arc
from arc.color import fg, bg, fx


def test_markdown_heading():
    assert (
        arc.markdown("# Hello, world!", arc.PresentConfig())
        == f"{fx.BOLD}HELLO, WORLD!{fx.CLEAR}\n"
    )


def test_paragraph():
    assert (
        arc.markdown(
            """
Paragraph one
more of the first paragraph

Paragraph two
""",
            arc.PresentConfig(),
        )
        == """\
    Paragraph one more of the first paragraph

    Paragraph two
"""
    )


def test_list():
    assert (
        arc.markdown(
            """
- one
- two
- three
""",
            arc.PresentConfig(indent=""),
        )
        == """\
  • one
  • two
  • three
"""
    )


def test_unformatted():

    assert (
        arc.markdown(
            """\
```
do not format this content at all
This should remain on this line
            This should remain on this line
                This should remain on this line
```
    """,
            arc.PresentConfig(),
        )
        == """\
do not format this content at all
This should remain on this line
            This should remain on this line
                This should remain on this line
"""
    )


def test_emphasis():
    assert (
        arc.markdown("*emphasis*", arc.PresentConfig(indent=""))
        == f"{fx.ITALIC}emphasis{fx.CLEAR}\n"
    )


def test_strong():
    assert (
        arc.markdown("**strong**", arc.PresentConfig(indent=""))
        == f"{fx.BOLD}strong{fx.CLEAR}\n"
    )


def test_strikethrogh():
    assert (
        arc.markdown("~~strikethrough~~", arc.PresentConfig(indent=""))
        == f"{fx.STRIKETHROUGH}strikethrough{fx.CLEAR}\n"
    )


def test_underline():
    assert (
        arc.markdown("__underline__", arc.PresentConfig(indent=""))
        == f"{fx.UNDERLINE}underline{fx.CLEAR}\n"
    )


def test_link():
    assert (
        arc.markdown("[www.example.com]", arc.PresentConfig(indent=""))
        == f"{fg.ARC_BLUE}{fx.UNDERLINE}www.example.com{fx.CLEAR}\n"
    )


def test_code():
    assert (
        arc.markdown("`code`", arc.PresentConfig(indent=""))
        == f"{bg.GREY}{fg.WHITE}code{fx.CLEAR}\n"
    )


def test_colored():
    config = arc.PresentConfig(indent="")
    assert (
        arc.markdown("[[fg.RED]]red[[/fg.RED]]", config) == f"{fg.RED}red{fx.CLEAR}\n"
    )

    assert (
        arc.markdown("[[bg.RED]]red[[/bg.RED]]", config) == f"{bg.RED}red{fx.CLEAR}\n"
    )

    assert (
        arc.markdown("[[color.accent]]red[[/color.accent]]", config)
        == f"{config.color.accent}red{fx.CLEAR}\n"
    )


def test_command_markdown():
    @arc.command("cli")
    def command(
        value: str = arc.Option(
            desc="""lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse"""
        ),
        value2: str = arc.Option(
            desc="""lorem ipsum dolor sit **amet** consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse"""
        ),
        value3: str = arc.Option(desc="thing", default="hi"),
    ):
        """
        Here's a description
        lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore
        et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi
        ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse

        # Heading 1
        Here's a paragraph.
        Here's a second line for that paragraph

        # Emphasis
        Here's a *second* paragraph

        # Bold
        Here's a **third** paragraph

        # Links
        Here's a link: [https://www.google.com]

        # Code
        Here's some code: `cli --help`

        # Strikethrough Text
        Here's some strikethrough: ~~strikethrough~~

        # Underlined Text
        Here's some underline: __underline__

        # Unformatted Text
        ```
        do not format this content at all
        This should remain on this line
                    This should remain on this line
                        This should remain on this line
        ```

        # List
        For example:

        - lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor
        incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud
        - **item 1**
        - *item 2*
        __ainfeianfeianfeianfein__
        - item 3

        # Colored Text

        - [[fg.RED]]red[[/fg.RED]]
        - [[color.subtle]]red[[/color.subtle]]
        """

    @command.subcommand
    def sub():
        """short desc

        some more desc
        """

    assert (
        command.doc.help()
        == "\x1b[1mUSAGE\x1b[0m\n    \x1b[38;2;59;192;240mcli\x1b[0m [-h] [--value3 VALUE3] --value VALUE --value2 VALUE2\n    \x1b[38;2;59;192;240mcli\x1b[0m \x1b[4m<subcommand>\x1b[0m [ARGUMENTS ...]\n\n\x1b[1mDESCRIPTION\x1b[0m\n    Here's a description lorem ipsum dolor sit amet consectetur adipiscing elit\n    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad\n    minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea\n    commodo consequat duis aute irure dolor in reprehenderit in voluptate velit\n    esse\n\n\x1b[1mOPTIONS\x1b[0m\n    \x1b[38;2;59;192;240m--help\x1b[0m\x1b[90m (-h)\x1b[0m  Displays this help message\n    \x1b[38;2;59;192;240m--value\x1b[0m      lorem ipsum dolor sit amet consectetur adipiscing elit sed do\n                 eiusmod tempor incididunt ut labore et dolore magna aliqua ut\n                 enim ad minim veniam quis nostrud exercitation ullamco\n                 laboris nisi ut aliquip ex ea commodo consequat duis aute\n                 irure dolor in reprehenderit in voluptate velit esse\n    \x1b[38;2;59;192;240m--value2\x1b[0m     lorem ipsum dolor sit \x1b[1mamet\x1b[0m consectetur adipiscing elit sed do\n                 eiusmod tempor incididunt ut labore et dolore magna aliqua ut\n                 enim ad minim veniam quis nostrud exercitation ullamco\n                 laboris nisi ut aliquip ex ea commodo consequat duis aute\n                 irure dolor in reprehenderit in voluptate velit esse\n    \x1b[38;2;59;192;240m--value3\x1b[0m     thing \x1b[90m(default: hi)\x1b[0m\n\n\x1b[1mSUBCOMMANDS\x1b[0m\n    \x1b[38;2;59;192;240msub\x1b[0m          short desc\n\n\x1b[1mHEADING 1\x1b[0m\n    Here's a paragraph. Here's a second line for that paragraph\n\n\x1b[1mEMPHASIS\x1b[0m\n    Here's a \x1b[3msecond\x1b[0m paragraph\n\n\x1b[1mBOLD\x1b[0m\n    Here's a \x1b[1mthird\x1b[0m paragraph\n\n\x1b[1mLINKS\x1b[0m\n    Here's a link: \x1b[38;2;59;192;240m\x1b[4mhttps://www.google.com\x1b[0m\n\n\x1b[1mCODE\x1b[0m\n    Here's some code: \x1b[100m\x1b[37mcli --help\x1b[0m\n\n\x1b[1mSTRIKETHROUGH TEXT\x1b[0m\n    Here's some strikethrough: \x1b[9mstrikethrough\x1b[0m\n\n\x1b[1mUNDERLINED TEXT\x1b[0m\n    Here's some underline: \x1b[4munderline\x1b[0m\n\n\x1b[1mUNFORMATTED TEXT\x1b[0m\ndo not format this content at all\nThis should remain on this line\n            This should remain on this line\n                This should remain on this line\n\n\x1b[1mLIST\x1b[0m\n    For example:\n\n      • lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod\n        tempor incididunt ut labore et dolore magna aliqua ut enim ad minim\n        veniam quis nostrud\n      • \x1b[1mitem 1\x1b[0m\n      • \x1b[3mitem 2\x1b[0m \x1b[4mainfeianfeianfeianfein\x1b[0m\n      • item 3\n\n\x1b[1mCOLORED TEXT\x1b[0m\n      • \x1b[31mred\x1b[0m\n      • \x1b[90mred\x1b[0m\n"
    )
