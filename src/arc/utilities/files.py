import os
from arc import Utility

files = Utility("files")


@files.script("create", options=["filename"])
def create(filename):
    '''Creates a a specified file
    :param filename: file to be created
    '''
    open(filename, "w+").close()


@files.script("read", options=["filename"])
def read(filename):
    '''Reads a specified file
    :param filename: file to be read
    '''
    with open(filename) as file:
        print(file.read())


@files.script("append", options=["filename", "write"])
def append(filename, write):
    '''Appends text to the specified file
    :param filename: file to be appended to
    :param write: text to write
    '''
    with open(filename, "a") as file:
        file.write(write)


@files.script("delete", options=["filename"])
def delete(filename):
    '''Deletes a specified file
    :param filename: file to be deleted
    '''
    os.remove(filename)
