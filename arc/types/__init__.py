import sys

from .aliases import Alias
from .convert import convert
from .dates import DateArgs, DateTimeArgs, TimeArgs
from .file import File, Stdin, StdinFile, Stream
from .network import (
    AllowedUrlProtocols,
    FtpUrl,
    HttpUrl,
    MysqlUrl,
    PostgresUrl,
    RequiredUrlComponents,
    Url,
    WebSocketUrl,
)
from .numbers import (
    AnyNumber,
    Binary,
    Hex,
    NegativeFloat,
    NegativeInt,
    Oct,
    PositiveFloat,
    PositiveInt,
)
from .path import DirectoryPath, FilePath, ValidPath
from .semver import SemVer
from .state import State
from .strings import Char, Email, Password
from .type_info import TypeInfo

if sys.platform not in ("win32", "cygwin", "emscripten"):
    from .users import Group, User

__all__ = [
    "Alias",
    "convert",
    "SemVer",
    "State",
    "TypeInfo",
    "DateArgs",
    "DateTimeArgs",
    "TimeArgs",
    "File",
    "Stdin",
    "StdinFile",
    "Stream",
    "AllowedUrlProtocols",
    "RequiredUrlComponents",
    "Url",
    "HttpUrl",
    "WebSocketUrl",
    "FtpUrl",
    "MysqlUrl",
    "PostgresUrl",
    "AnyNumber",
    "Binary",
    "Oct",
    "Hex",
    "NegativeFloat",
    "NegativeInt",
    "PositiveFloat",
    "PositiveInt",
    "DirectoryPath",
    "FilePath",
    "ValidPath",
    "Char",
    "Email",
    "Password",
    "User",
    "Group",
]
