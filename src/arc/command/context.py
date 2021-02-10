class Context(dict):
    def __repr__(self):
        return f"<Context : {len(self)}>"

    def __getattr__(self, attr):
        return self[attr]
