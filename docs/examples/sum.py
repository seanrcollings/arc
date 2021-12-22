import arc


@arc.command()
def main(nums: list[int] = []):
    if not nums:
        print("Provide some integers to sum up")
    else:
        total = 0
        for val in nums:
            total += val
        print("The total is: ", total)


main()