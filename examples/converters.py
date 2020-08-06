"""
Example CLI to demonstrate all of the type converters
"""
from arc import CLI

cli = CLI()


# python3 converters.py int value=5 -> int
# python3 converters.py int value=hi -> error
@cli.script("int", options=["<int:value>"])
def int_type(value):
    """Demonstrates int conversion"""
    print(type(value))
    print(value)


# python3 converters.py byte value=5 -> bytes
# python3 converters.py byte value=hi -> bytes
@cli.script("byte", options=["<byte:value>"])
def byte_type(value):
    """Demonstrates byte conversion"""
    print(type(value))
    print(value)


# python3 converters.py float value=5 -> float
# python3 converters.py float value=5.5 -> float
# python3 converters.py int value=hi -> error
@cli.script("float", options=["<float:value>"])
def float_type(value):
    """Demonstrates float conversion"""
    print(type(value))
    print(value)


# python3 converters.py bool value=5 -> True
# python3 converters.py bool value=0 -> True
# python3 converters.py bool value=hi -> True
# python3 converters.py bool value="" -> False
@cli.script("bool", options=["<bool:value>"])
def bool_type(value):
    """Demonstrates bool conversion"""
    print(type(value))
    print(value)


# python3 converters.py bool value=True -> True
# python3 converters.py bool value=true -> True
# python3 converters.py bool value=False -> False
# python3 converters.py bool value=false -> False
# python3 converters.py bool value=ainfea -> error
@cli.script("sbool", options=["<sbool:value>"])
def sbool_type(value):
    """Demonstrates bool conversion"""
    print(type(value))
    print(value)


# python3 converters.py bool value=0 -> False
# python3 converters.py bool value=1 -> True
# python3 converters.py bool value=4 -> True
# python3 converters.py bool value=1231 -> True
# python3 converters.py bool value=afeafa -> error
@cli.script("ibool", options=["<ibool:value>"])
def ibool_type(value):
    """Demonstrates bool conversion"""
    print(type(value))
    print(value)


# python3 converters.py list value=1,2,3,4,5 -> ['1', '2', '3', '4', '5'] # Without spaces, you don't need quotation marks
# python3 converters.py list value="1, 2, 3, 4, 5" -> error, spaces not allowed
@cli.script("list", options=["<list:value>"])
def list_type(value):
    """Demonstrates bool conversion"""
    print(type(value))
    print(value)


if __name__ == "__main__":
    cli()
