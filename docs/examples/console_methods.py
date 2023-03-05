from arc.present.console import Console


console = Console()
console.print("Hi there!")
console.log("This is a log")
console.ok("Looks good!")
console.act("Time to take action!")
console.warn("Something is amiss")
console.error("Something has gone wrong")
console.subtle("This is a subtle message")
console.snake("Hisss")

with console.indent():
    console.print("I will be indented")

    with console.indent():
        console.print("I will be more indented")
