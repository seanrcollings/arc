from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Tuple
import subprocess
import os

EXECUTE = "EXECUTE"
FRAGMENT = "FRAGMENT"
OUTPUT = "OUTPUT"


class CodeBlock:
    def __init__(self, meta: str, code: str):
        split = meta.strip().split(" ")
        self.lang = split[0]
        self.fragment_index = 0

        if len(split) == 2:
            _type = split[1]
            if _type.isnumeric():
                self.fragment_index = int(_type)
                self.type = FRAGMENT

        else:
            if self.lang == "out":
                self.type = OUTPUT

            else:
                self.type = EXECUTE

        self.code = code

    def __str__(self):
        return (
            f"Directive: {self.lang} : {self.type}\n"
            "------------------\n"
            f"{self.code}\n"
            "------------------\n"
        )


@dataclass
class IO:
    command: str
    output: str


class Executable:
    def __init__(self, exec_components: List[CodeBlock], output: List[CodeBlock]):
        self.code: str = self.parse_exec(exec_components)
        self.tests: List[IO] = self.parse_output(output)

    def run(self):
        for io in self.tests:
            with self.create_file():

                out = subprocess.run(
                    ["python", "example.py", "hello"],
                    check=True,
                    stdout=subprocess.PIPE,
                )

                print(out.stdout.decode("utf-8").strip("\n") == io.output)

            # print(out.decode("utf-8").strip("\n"), io.output)
            # print(out.decode("utf-8") == io.output)

    @contextmanager
    def create_file(self):
        file = open("example.py", "w+")
        file.write(self.code)
        file.close()
        try:
            yield file
        finally:
            pass
            os.remove("example.py")

    @staticmethod
    def parse_exec(comp: List[CodeBlock]) -> str:
        return "\n\n".join([e.code for e in comp])

    @staticmethod
    def parse_output(output: List[CodeBlock]) -> List[IO]:
        tests: List[IO] = []
        for output_block in output:
            lines = output_block.code.splitlines()
            command = lines[0].strip("$").strip()
            data = "\n".join(lines[1:])
            tests.append(IO(command, data))
        return tests
