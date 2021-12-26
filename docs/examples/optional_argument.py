from typing import Optional
from arc import CLI

cli = CLI()


@cli.command()
def c1(val: Optional[int]):
    print(val)


@cli.command()
def c2(val: int = None):
    print(val)


cli()