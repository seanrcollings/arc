# Arc Types
Arc ships with a series of custom types that input can be converted into

## File Type
A file type will take in a file path and return a file handler object
```py x
from arc import CLI
from arc.types import File
cli = CLI()

@cli.command()
def file_test(file=File[File.READ]): # file will be of custom type File, but has the same interface as the TextIOWrapper returned by open()
    print(file.readlines())
```
The format for a File types is File[<FILE_MODE>] with the available file modes being:
  - READ
  - WRITE
  - APPEND
  - CREATE

Arc should handle the file cleanup process, however if you want to control when the file closes, you can with `file.close()`. Additionally, the file object implements `__enter__` and `__exit__` so can be used as a context manager.
```py
from arc import CLI
from arc.types import File
cli = CLI()

@cli.command()
def file_test(file=File[File.READ]):
    print(file.readlines())
    file.close()

    # OR

    with file as f:
        print(f.readlines())

    # With either approach, file will defintely be closed at this point

# unless something goes horribly wrong, once the function finishes execution ARC will close the file for you though.
```

