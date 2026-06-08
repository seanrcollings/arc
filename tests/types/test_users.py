import grp
import os
import pwd

import pytest

import arc
from arc import errors, types


def _first_user() -> pwd.struct_passwd:
    return pwd.getpwall()[0]


def _first_group() -> grp.struct_group:
    return grp.getgrall()[0]


class TestUsage:
    def test_user(self):
        @arc.command
        def command(user: types.User):
            return user

        u = _first_user()
        assert command(u.pw_name).name == u.pw_name
        assert command(str(u.pw_uid)).name == u.pw_name

        with pytest.raises(errors.InvalidParamValueError):
            command("invalid")

    def test_group(self):
        @arc.command
        def command(group: types.Group):
            return group

        g = _first_group()
        assert command(g.gr_name).name == g.gr_name
        assert command(str(g.gr_gid)).name == g.gr_name

        with pytest.raises(errors.InvalidParamValueError):
            command("invalid")


class TestUtilites:
    def test_equality(self):
        u1 = types.User("user1", "x", 1, 2, 3, "/home/user1", "shell")
        u2 = types.User("user2", "x", 1, 2, 3, "/home/user1", "shell")
        u3 = types.User("user3", "x", 19, 2, 3, "/home/user1", "shell")

        assert u1 == u2
        assert u1 != u3 != u2

        g1 = types.Group("group1", "x", 1)
        g2 = types.Group("group2", "x", 1)
        g3 = types.Group("group3", "x", 2)
        assert g1 == g2
        assert g1 != g3 != g2

    @pytest.mark.skip("Not working for now")
    def test_user_groups(self):
        if not os.environ.get("GITHUB_ACTIONS"):
            user = types.User(*pwd.getpwall()[0])
            groups = [types.Group(*g) for g in grp.getgrall() if user.name in g.gr_mem]
            assert user.group in groups
            assert [g in groups for g in user.groups]

    @pytest.mark.skip("Not working for now")
    def test_group_members(self):
        group = types.Group(*grp.getgrgid(1))
        users = [types.User(*pwd.getpwnam(m)) for m in group._mem]
        assert group.members == users

    @pytest.mark.skip("Not working for now")
    def test_contains(self):
        if not os.environ.get("GITHUB_ACTIONS"):
            group = types.Group(*grp.getgrgid(1))
            user = group.members[0]

            assert user in group
            assert user.name in group
            assert user.id in group
