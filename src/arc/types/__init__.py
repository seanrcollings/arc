from .arc_generic import ArcGeneric
from .file import File


def needs_cleanup(kind):
    return kind in (File,)
