"""Provides support for async reading and writing to stdin and stdout
mostly derived from https://github.com/vxgmichel/aioconsole
"""
# pylint: disable=protected-access
import sys
import asyncio


class StandardStreamReaderProtocol(asyncio.StreamReaderProtocol):
    def connection_made(self, transport):
        if self._stream_reader._transport is not None:  # type: ignore
            return
        super().connection_made(transport)


def protect_standard_streams(stream):
    if stream._transport is None:
        return
    try:
        fileno = stream._transport.get_extra_info("pipe").fileno()
    except (ValueError, OSError):
        return
    if fileno < 3:
        stream._transport._pipe = None


class StandardStreamReader(asyncio.StreamReader):
    __del__ = protect_standard_streams

    # @typing.no_type_check
    # async def readuntil(self, separator=b"\n"):
    #     # Re-implement `readuntil` to work around self._limit.
    #     # The limit is still useful to prevent the internal buffer
    #     # from growing too large when it's not necessary, but it
    #     # needs to be disabled when the user code is purposely
    #     # reading from stdin.
    #     while True:
    #         try:
    #             return await super().readuntil(separator)
    #         except asyncio.LimitOverrunError as e:
    #             if self._buffer.startswith(separator, e.consumed):
    #                 chunk = self._buffer[: e.consumed + len(separator)]
    #                 del self._buffer[: e.consumed + len(separator)]
    #                 self._maybe_resume_transport()
    #                 return bytes(chunk)
    #             await self._wait_for_data("readuntil")


class StandardStreamWriter(asyncio.StreamWriter):

    __del__ = protect_standard_streams

    def write(self, data):
        if isinstance(data, str):
            data = data.encode()
        super().write(data)


async def get_streams():
    loop = asyncio.get_event_loop()
    reader = StandardStreamReader(loop=loop)
    protocol = StandardStreamReaderProtocol(reader, loop=loop)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    writer_transport, _ = await loop.connect_write_pipe(lambda: protocol, sys.stdout)
    writer = StandardStreamWriter(writer_transport, protocol, reader, loop)

    return reader, writer
