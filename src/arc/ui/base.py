import abc
import sys
import asyncio
import tty
import termios
from typing import Tuple, Union, cast, Any

from . import utils
from . import keys
from . import streams


class UIBase(abc.ABC):
    def __init__(self):
        self.should_update = True
        self.running = True
        self.__old_settings = termios.tcgetattr(sys.stdin.fileno())
        self.reader = None
        self.writer = None
        self.return_value = None

    def run(self):
        self.setup()
        try:
            asyncio.get_event_loop().run_until_complete(
                asyncio.wait([self.__update(), self.__render()])
            )
        except KeyboardInterrupt:
            ...

        self.teardown()
        return self.return_value

    def setup(self):
        fd = sys.stdin.fileno()
        tty.setcbreak(fd)
        utils.hide_cursor()
        utils.clear()

    def teardown(self):
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, self.__old_settings)
        utils.clear()
        utils.show_cursor()
        utils.home_pos()

    def done(self, value: Any = None):
        self.return_value = value
        self.running = False

    async def getkey(self, i: int = 1) -> Union[int, Tuple[int, ...]]:
        reader = cast(streams.StandardStreamReader, self.reader)
        data = await reader.read(i)
        key = ord(data.decode("utf-8"))
        return key

    async def __update(self):
        if not self.reader or self.writer:
            self.reader, self.writer = await streams.get_streams()

        while self.running:
            key = await self.getkey()
            if key == keys.q:
                self.running = False
            else:
                self.should_update = await self.update(key)

    async def update(self, key: Union[int, Tuple[int, ...]]) -> bool:
        """Determines whether or not the
        next render cycle should occur.
        """
        return False

    async def __render(self):
        while self.running:
            if self.should_update:
                utils.home_pos()
                await self.render()
            await asyncio.sleep(0.016)

    @abc.abstractmethod
    async def render(self):
        """Renders out the UI element
        is called every time `update` return true
        """
