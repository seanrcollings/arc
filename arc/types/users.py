from __future__ import annotations
import pwd
import grp
import functools
import pathlib

from arc import errors, utils, autocompletions as ac


class User(
    utils.Display, members=["name", "id", "group_id", "gecos", "directory", "shell"]
):
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

    @classmethod
    def __convert__(cls, value):
        users = {p[0]: p for p in pwd.getpwall()}

        if value in users:
            return cls(*users[value])

        raise errors.ConversionError(value, f"{value} is not a valid user")

    @classmethod
    def __completions__(cls, info: ac.CompletionInfo, *_args, **_kwargs):
        return ac.Completion(info.current, ac.CompletionType.USERS)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.id == other.id

        return NotImplemented

    @classmethod
    def all(cls):
        return [cls(*g) for g in pwd.getpwall()]

    @functools.cached_property
    def group(self):
        group = grp.getgrgid(self.group_id)
        return Group(*group)

    @functools.cached_property
    def groups(self):
        return [Group(*g) for g in grp.getgrall() if self.name in g.gr_mem]


class Group(utils.Display, members=["name", "id", "members"]):
    def __init__(
        self, name: str, password: str | None, gid: int, mem: list[str] = None
    ) -> None:
        self.name = name
        self.password = password
        self.id = gid
        self._mem = mem or []

    @classmethod
    def __convert__(cls, value):
        groups = {p[0]: p for p in grp.getgrall()}

        if value in groups:
            return cls(*groups[value])

        raise errors.ConversionError(value, f"{value} is not a valid group")

    @classmethod
    def __completions__(cls, info: ac.CompletionInfo, *_args, **_kwargs):
        return ac.Completion(info.current, ac.CompletionType.GROUPS)

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
    def all(cls):
        return [cls(*g) for g in grp.getgrall()]

    @functools.cached_property
    def members(self):
        return [User(*pwd.getpwnam(m)) for m in self._mem]
