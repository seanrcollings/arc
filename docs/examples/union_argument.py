from typing import Union
import arc


@arc.command()
def main(number: Union[int, str]):
    print(type(number))


main()
