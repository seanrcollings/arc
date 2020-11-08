class File:
    def __init__(self, mode):
        self.mode = mode
        self.file_path = None
        self.__file_handle = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exception_type, value, traceback):
        self.__file_handle.close()

    def __getattr__(self, attr):
        return getattr(self.__file_handle, attr)

    def open(self, file_path=None):
        self.file_path = file_path or self.file_path

        self.__file_handle = open(self.file_path, self.mode)
        return self
