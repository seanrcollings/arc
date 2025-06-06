from __future__ import annotations
import typing as t
import functools
import grp
import pathlib
import pwd

from arc import autocompletions as ac, utils
from arc import errors


class User:
    def __init__(
        self,
        name: str,
        password: str,
        uid: int,
        gid: int,
        gecos: str,
        directory: str,
        shell: str,
    ):
        self.name = name
        self.password = password
        self.id = uid
        self.group_id = gid
        self.gecos = gecos
        self.directory = pathlib.Path(directory)
        self.shell = pathlib.Path(shell)

    __repr__ = utils.display("name", "id", "group_id", "gecos", "directory", "shell")

    @classmethod
    def __convert__(cls, value: str) -> User:
        users = pwd.getpwall()

        for user in users:
            if user.pw_name == value or str(user.pw_uid) == value:
                return cls(*user)

        raise errors.ConversionError(value, f"{value} is not a valid user")

    @classmethod
    def __completions__(
        cls, info: ac.CompletionInfo, *_args: t.Any, **_kwargs: t.Any
    ) -> t.Iterable[ac.Completion]:
        yield ac.Completion(info.current, type=ac.CompletionType.USERS)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.id == other.id

        return NotImplemented

    @classmethod
    def all(cls) -> list[User]:
        return [cls(*g) for g in pwd.getpwall()]

    @functools.cached_property
    def group(self) -> Group:
        group = grp.getgrgid(self.group_id)
        return Group(*group)

    @functools.cached_property
    def groups(self) -> list[Group]:
        return [Group(*g) for g in grp.getgrall() if self.name in g.gr_mem]


class Group:
    def __init__(
        self, name: str, password: str | None, gid: int, mem: list[str] = None
    ) -> None:
        self.name = name
        self.password = password
        self.id = gid
        self._mem = mem or []

    __repr__ = utils.display("name", "id", "members")

    @classmethod
    def __convert__(cls, value: str) -> Group:
        groups = grp.getgrall()

        for group in groups:
            if group.gr_name == value or str(group.gr_gid) == value:
                return cls(*group)

        raise errors.ConversionError(value, f"{value} is not a valid group")

    @classmethod
    def __completions__(
        cls, info: ac.CompletionInfo, *_args: t.Any, **_kwargs: t.Any
    ) -> t.Iterable[ac.Completion]:
        yield ac.Completion(info.current, type=ac.CompletionType.GROUPS)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Group):
            return self.id == other.id

        return NotImplemented

    def __contains__(self, item: str | int | User) -> bool:
        if isinstance(item, User):
            return item.name in self._mem
        elif isinstance(item, str):
            return item in self._mem
        elif isinstance(item, int):
            user = pwd.getpwuid(item)
            return user.pw_name in self._mem

    @classmethod
    def all(cls) -> list[Group]:
        return [cls(*g) for g in grp.getgrall()]

    @functools.cached_property
    def members(self) -> list[User]:
        return [User(*pwd.getpwnam(m)) for m in self._mem]
