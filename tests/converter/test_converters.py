from tests.base_test import BaseTest


class TestConverters(BaseTest):
    def setUp(self):
        self.cli = self.create_cli()

    def test_string(self):
        func = self.create_script(self.cli, "string", lambda name: name)
        self.cli("string name=Sean")
        func.assert_called_with(name="Sean")

    def test_int(self):
        func = self.create_script(
            self.cli, "int", lambda number: number, annotations={"number": int}
        )
        self.cli("int number=5")
        func.assert_called_with(number=5)

    def test_float(self):
        func = self.create_script(
            self.cli, "float", lambda number: number, annotations={"number": float}
        )
        self.cli("float number=4.5")
        func.assert_called_with(number=4.5)

    def test_byte(self):
        func = self.create_script(
            self.cli, "byte", lambda string: string, annotations={"string": bytes}
        )
        self.cli("byte string=hello")
        func.assert_called_with(string=b"hello")

    def test_list(self):
        func = self.create_script(
            self.cli, "list", lambda test: test, annotations={"test": list}
        )
        self.cli("list test=1,2,3,4")
        func.assert_called_with(test=["1", "2", "3", "4"])

    def test_bool(self):
        func = self.create_script(
            self.cli, "bool", lambda yes: yes, annotations={"yes": bool}
        )
        true_values = [1, 2, 111, "true", "t"]
        for value in true_values:
            self.cli(f"bool yes={value}")
            func.assert_called_with(yes=True)

        false_values = [0, "false", "f"]
        for value in false_values:
            self.cli(f"bool yes={value}")
            func.assert_called_with(yes=False)

    # def test_invalid_converters(self):
    #     func = MagicMock()
    #     with self.assertRaises(ArcError):
    #         self.cli.script(name="string",
    #                    options=["<str:name><int:name>"])(function=func)
    #     with self.assertRaises(ArcError):
    #         self.cli.script(name="string", options=["<str::name>"])(function=func)
