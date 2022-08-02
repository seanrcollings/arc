import arc


@arc.command()
def main(nums: list[int]):
    arc.print("The total is: ", sum(nums))


main()
