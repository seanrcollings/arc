import os
import pytest
from arc import types, CLI, errors
import pwd
import grp


class TestUsage:
    def test_user(self, cli: CLI):
        @cli.command()
        def test_user(user: types.User):
            return user

        assert cli("test-user root").name == "root"

        with pytest.raises(errors.InvalidParamaterError):
            cli("test-user invalid")

    def test_group(self, cli: CLI):
        @cli.command()
        def test_group(user: types.Group):
            return user

        assert cli("test-group root").name == "root"

        with pytest.raises(errors.InvalidParamaterError):
            cli("test-group invalid")


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

    def test_user_groups(self):
        if not os.environ.get("GITHUB_ACTIONS"):
            user = types.User(*pwd.getpwall()[0])
            groups = [types.Group(*g) for g in grp.getgrall() if user.name in g.gr_mem]
            assert user.group in groups
            assert [g in groups for g in user.groups]

    def test_group_members(self):
        group = types.Group(*grp.getgrgid(1))
        users = [types.User(*pwd.getpwnam(m)) for m in group._mem]
        assert group.members == users

    def test_contains(self):
        if not os.environ.get("GITHUB_ACTIONS"):
            group = types.Group(*grp.getgrgid(1))
            user = group.members[0]

            assert user in group
            assert user.name in group
            assert user.id in group
