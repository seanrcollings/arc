from typing import Literal
import arc


@arc.command
def main(word: Literal["foo", "bar", 1]):
    arc.print(word, type(word))


main()
