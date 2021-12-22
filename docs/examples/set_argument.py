import arc


@arc.command()
def main(vals: set):
    print("Unique values:")
    print("\n".join(vals))


main()