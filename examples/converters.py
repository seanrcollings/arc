"""Example CLI to demonstrate all of the type converters"""
from typing import List
from arc import CLI

cli = CLI()


# python3 converters.py int value=5 -> int
# python3 converters.py int value=hi -> error
@cli.script("int")
def int_type(value: int):
    """Demonstrates int conversion"""
    print(type(value))
    print(value)


# python3 converters.py byte value=5 -> bytes
# python3 converters.py byte value=hi -> bytes
@cli.script("byte")
def byte_type(value: bytes):
    """Demonstrates byte conversion"""
    print(type(value))
    print(value)


# python3 converters.py float value=5 -> float
# python3 converters.py float value=5.5 -> float
# python3 converters.py int value=hi -> error
@cli.script("float")
def float_type(value: float):
    """Demonstrates float conversion"""
    print(type(value))
    print(value)


# python3 converters.py list value=1,2,3,4,5 -> ['1', '2', '3', '4', '5'] # Without spaces, you don't need quotation marks
# python3 converters.py list value="1, 2, 3, 4, 5" -> error, spaces not allowed
@cli.script("list")
def list_type(value: List[int]):
    """Demonstrates bool conversion"""
    print(type(value))
    print(value)


if __name__ == "__main__":
    cli()
