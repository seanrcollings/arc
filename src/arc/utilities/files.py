import os
from arc import Utility

files = Utility("files")


@files.script("read", options=["filename"])
def read(filename):
    '''
    Reads a specified file
    :param filename: file to be read
    '''
    with open(filename) as file:
        print(file.read())


@files.script("delete", options=["filename"])
def delete(filename):
    '''
    Deletes a specified file
    :param filename: file to be deleted
    '''
    os.remove(filename)
