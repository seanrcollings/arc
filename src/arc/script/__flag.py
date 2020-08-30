class Flag:
    def __init__(self, param):
        self.name = param.name
        if param.default is param.empty:
            self.value = False
        else:
            self.value = param.default
