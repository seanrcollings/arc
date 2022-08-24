import arc


@arc.command()
def main(*, names: list):
    for name in names:
        arc.print(name)


main()
