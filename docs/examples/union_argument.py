from typing import Union
import arc


@arc.command()
def main(number: Union[int, str]):
    arc.print(type(number))


main()
