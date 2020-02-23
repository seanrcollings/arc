# Context Managers

## What are context managers?
I would recommend checking out this [Python Tips](https://book.pythontips.com/en/latest/context_managers.html) article for a more in depth explanation, but here's a quick rundown
Context Managers allow you to allocate a resourece withing a specified block of code, then release it when the block completes, even if it throws an exception. This is commonly used for opening files in Python, because now you don't have to worry about closing them after


### This
```py
file = open("file.txt")
print(file.read())
file.close()
```
### Becomes this
```py
with open("file.txt") as file:
    print(file.read())
# no need for that file.close()!
```

## Context managers in Arc
Arc supports the use of context managers for it's CLI level scripts and utility scripts. This means you can have access to this resource during the execution of any of the scripts, and have it released at the end of the script for you.

### Arc script without using context managers
```py
from arc import CLI

cli = CLI()

@cli.script("read")
def hello():
    '''Reads the example.txt file in the current directory'''
    file = open("example.txt")
    print(file.read())
    file.close()

    # Or using with syntax
    with open("example.txt") as file:
        print(file.read())

cli()
```

### Arc script using context managers
```py
from arc import CLI

cli = CLI(context_manager=open("file.txt"))

@cli.script("read")
def hello(file):
    '''Reads the example.txt file in the current directory'''
    print(file.read())

cli()
```

That's all there is to it! Once your script completes it's execution, Arc will release the managed resource for you safely. This can be applied at both top level scripts, and utility scripts.
