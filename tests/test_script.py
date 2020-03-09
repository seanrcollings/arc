'''Test the functionality of the Script class'''
from unittest.mock import patch, MagicMock
import importlib
from tests.base_test import BaseTest
from arc.script import Script
from arc.errors import ExecutionError, ArcError


class TestScript(BaseTest):
    def create_script(self,
                      options=None,
                      flags=None,
                      pass_args=False,
                      pass_kwargs=False):
        func = MagicMock()
        return Script(name="test",
                      function=func,
                      options=options,
                      flags=flags,
                      pass_args=pass_args,
                      pass_kwargs=pass_kwargs)

    def test_execution(self):
        script = self.create_script(options=["x", "<int:y>"], flags=["--test"])

        script(user_input=["x=2", "y=3"])
        script.function.assert_called_with(x="2", y=3, test=False)

        script(user_input=["x=2", "y=3", "--test"])
        script.function.assert_called_with(x="2", y=3, test=True)

    def test_build_flags(self):
        script = self.create_script(options=["x", "<int:y>"], flags=["--test"])
        assert "test" in script.flags

        with self.assertRaises(ArcError):
            script = self.create_script(options=["x", "<int:y>"],
                                        flags=["++test"])

    def test_nonexistant_options(self):
        script = self.create_script(options=["x", "<int:y>"], flags=["--test"])
        with self.assertRaises(ExecutionError):
            script(user_input=["p=2"])

    def test_nonexistant_flag(self):
        script = self.create_script(options=["x", "<int:y>"], flags=["--test"])
        with self.assertRaises(ExecutionError):
            script(user_input=["--none"])

    def test_pass_args(self):
        script = self.create_script(pass_args=True)
        script(user_input=["hello", "there=are", "being passed"])
        script.function.assert_called_with(
            "hello",
            "there=are",
            "being passed",
        )

        with self.assertRaises(ArcError):
            script = self.create_script(options=["option"], pass_args=True)

    def test_pass_kwargs(self):
        script = self.create_script(pass_kwargs=True)
        script(user_input=["option=value", "option2=value2", "option3=value3"])
        script.function.assert_called_with(option="value",
                                           option2="value2",
                                           option3="value3")

        with self.assertRaises(ArcError):
            script = self.create_script(options=["option"], pass_kwargs=True)
