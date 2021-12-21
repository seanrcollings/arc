import os
from arc import namespace

files = namespace("files")


@files.subcommand("create")
def create(filename):
    """Creates a a specified file
    :param filename: file to be created
    """
    open(filename, "w+").close()


@files.subcommand("read")
def read(filename):
    """Reads a specified file
    :param filename: file to be read
    """
    with open(filename) as file:
        print(file.read())


@files.subcommand("append")
def append(filename, write):
    """Appends text to the specified file
    :param filename: file to be appended to
    :param write: text to write
    """
    with open(filename, "a") as file:
        file.write(write)


@files.subcommand("delete")
def delete(filename):
    """Deletes a specified file
    :param filename: file to be deleted
    """
    os.remove(filename)
