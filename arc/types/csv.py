from __future__ import annotations
from collections.abc import Iterable
import contextlib
import csv
import _csv
import typing as t

from arc.types.type_arg import TypeArg
from arc.types.type_info import TypeInfo

_DialectLike = t.Union[str, csv.Dialect, type[csv.Dialect]]


class CSVReader(t.Protocol):
    line_num: int

    @property
    def dialect(self) -> csv.Dialect: ...

    def __iter__(self) -> t.Self: ...
    def __next__(self) -> t.List[str]: ...

    @classmethod
    def __convert__(
        cls, value: str, info: TypeInfo[CSVReader]
    ) -> t.ContextManager[_csv._reader]:

        args = t.cast(CSVReader.Args, info.type_arg or CSVReader.Args())

        # arc automatically opens context managers when the command
        # is called and closes them when the command is done.
        @contextlib.contextmanager
        def open_csv(
            path: str, args: CSVReader.Args
        ) -> t.Generator[_csv._reader, None, None]:
            with open(path, "r", newline="") as f:
                reader = csv.reader(f, args.dialect, **args.dict())
                yield reader

        return open_csv(value, args)

    class Args(TypeArg):
        __slots__ = (
            "dialect",
            "delimiter",
            "quotechar",
            "escapechar",
            "doublequote",
            "skipinitialspace",
            "lineterminator",
            "quoting",
            "strict",
        )

        def __init__(
            self,
            dialect: _DialectLike = "excel",
            *,
            delimiter: str = ",",
            quotechar: str | None = '"',
            escapechar: str | None = None,
            doublequote: bool = True,
            skipinitialspace: bool = False,
            lineterminator: str = "\r\n",
            quoting: int = 0,
            strict: bool = False,
        ):
            self.dialect = dialect
            self.delimiter = delimiter
            self.quotechar = quotechar
            self.escapechar = escapechar
            self.doublequote = doublequote
            self.skipinitialspace = skipinitialspace
            self.lineterminator = lineterminator
            self.quoting = quoting
            self.strict = strict

        def dict(self, unwrap_defaults: bool = True) -> dict[str, t.Any]:
            dct = super().dict(unwrap_defaults)
            del dct["dialect"]
            return dct


class CSVWriter(t.Protocol):
    @property
    def dialect(self) -> csv.Dialect: ...

    def writerow(self, row: Iterable[t.Any], /) -> t.Any: ...
    def writerows(self, rows: Iterable[Iterable[t.Any]], /) -> None: ...

    @classmethod
    def __convert__(
        cls, value: str, info: TypeInfo[CSVWriter]
    ) -> t.ContextManager[_csv._writer]:

        args = t.cast(CSVWriter.Args, info.type_arg or CSVWriter.Args())

        @contextlib.contextmanager
        def open_csv(
            path: str, args: CSVWriter.Args
        ) -> t.Generator[_csv._writer, None, None]:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f, args.dialect, **args.dict())
                yield writer

        return open_csv(value, args)

    class Args(TypeArg):
        __slots__ = (
            "dialect",
            "delimiter",
            "quotechar",
            "escapechar",
            "doublequote",
            "skipinitialspace",
            "lineterminator",
            "quoting",
            "strict",
        )

        def __init__(
            self,
            dialect: _DialectLike = "excel",
            *,
            delimiter: str = ",",
            quotechar: str = '"',
            escapechar: str | None = None,
            doublequote: bool = True,
            skipinitialspace: bool = False,
            lineterminator: str = "\r\n",
            quoting: int = 0,
            strict: bool = False,
        ):
            self.dialect = dialect
            self.delimiter = delimiter
            self.quotechar = quotechar
            self.escapechar = escapechar
            self.doublequote = doublequote
            self.skipinitialspace = skipinitialspace
            self.lineterminator = lineterminator
            self.quoting = quoting
            self.strict = strict

        def dict(self, unwrap_defaults: bool = True) -> dict[str, t.Any]:
            dct = super().dict(unwrap_defaults)
            del dct["dialect"]
            return dct
