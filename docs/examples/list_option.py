import arc


@arc.command()
def main(*, names: list = []):
    if not names:
        arc.print("No names :(")
    else:
        for name in names:
            arc.print(name)


main()
