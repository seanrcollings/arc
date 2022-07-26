import os
import sys
import contextlib


@contextlib.contextmanager
def environ(**env: str):
    copy = os.environ.copy()
    os.environ.clear()
    os.environ.update(env)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(copy)
