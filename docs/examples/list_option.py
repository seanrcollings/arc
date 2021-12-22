import arc


@arc.command()
def main(*, names: list = []):
    if not names:
        print("No names :(")
    else:
        for name in names:
            print(name)


main()