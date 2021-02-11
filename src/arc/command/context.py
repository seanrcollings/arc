class Context(dict):
    def __repr__(self):
        return f"<Context : {' '.join(key + '=' + str(value) for key, value in self.items())}>"

    def __getattr__(self, attr):
        return self[attr]
