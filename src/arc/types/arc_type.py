class ArcType(type):
    def __getitem__(cls, *args):
        return cls(*args)
