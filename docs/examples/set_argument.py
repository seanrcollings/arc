import arc


@arc.command
def main(vals: set):
    arc.print("Unique values:")
    arc.print("\n".join(vals))


main()
