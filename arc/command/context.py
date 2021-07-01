"""
.. include:: ../../wiki/Context.md
"""


class Context(dict):
    """Context object, extends `dict`"""

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f" : {' '.join(key + '=' + str(value) for key, value in self.items())}>"
        )

    def __getattr__(self, attr):
        return self[attr]
