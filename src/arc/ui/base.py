import datetime
import sys
import threading

from . import utils
from . import keys


class UIBase:
    def __init__(self):
        self.should_update = True
        self.running = True
        self.update_thread = threading.Thread(target=self.__update)
        self.render_thread = threading.Thread(target=self.__render)

    def run(self):
        self.update_thread.start()
        self.render_thread.start()

    def stop(self):
        self.running = False
        # self.update_thread.join()
        # self.render_thread.join()

    def __update(self):
        while self.running:
            key = ord(utils.getch())
            if key == keys.q:
                self.stop()
                sys.exit(0)
            self.should_update = self.update(key)

    def update(self, key: int) -> bool:
        """Determines whether or not the
        next render cycle should occur.
        """
        return True

    def __render(self):
        utils.clear()
        while self.running:
            utils.home_pos()
            if self.should_update:
                self.render()

    def render(self):
        """Renders out the UI element
        is called every time `update` return true
        """
        print(datetime.datetime.now())
