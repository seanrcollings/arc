from arc.utils import Helpful
from arc import config


class Flag(Helpful):
    def __init__(self, param):
        self.name = param.name
        if param.default is param.empty:
            self.value = False
        else:
            self.value = param.default

    def __str__(self):
        return f"--{self.name} {self.value}"

    def __repr__(self):
        return f"<Flag : {self.name} : {self.value}>"

    def reverse(self):
        self.value = not self.value
        return self

    def helper(self):
        print(f"{config.flag_denoter}{self.name}={self.value}")
