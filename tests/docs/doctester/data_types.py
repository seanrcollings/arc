import os
import shlex
import subprocess
from typing import List, Optional
from dataclasses import dataclass
from contextlib import contextmanager


EXECUTE = "EXECUTE"
FRAGMENT = "FRAGMENT"
OUTPUT = "OUTPUT"


class CodeBlock:
    def __init__(self, meta: str, code: str, file_name: str):
        split = meta.strip().split(" ")
        self.lang = split[0]
        self.fragment_index = 0
        self.file_name = file_name

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
class Command:
    exe: str
    file: str
    args: List[str]

    def __str__(self):
        return f"{self.exe} {self.file} {' '.join(self.args)}"


@dataclass
class IO:
    command: Command
    output: str


class Executable:
    def __init__(self, exec_components: List[CodeBlock], output: List[CodeBlock]):
        self.code: str = self.parse_exec(exec_components)
        self.tests: List[IO] = self.parse_output(output)
        self.origin = exec_components[0].file_name
        self.result: Optional[str] = None
        super().__init__()

    def execute(self):
        if len(self.tests) == 0:
            return True, True
        for io in self.tests:
            with self.create_file(io):
                # print(f"Executing command: [{str(io.command)}]")
                out = subprocess.run(
                    [io.command.exe, io.command.file, *io.command.args],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.result = out.stdout.decode("utf-8").strip("\n")
                return self.result, io.output

    @contextmanager
    def create_file(self, io: IO):
        file = open(io.command.file, "w+")
        file.write(self.code)
        file.close()
        try:
            yield file
        finally:
            os.remove(io.command.file)

    @staticmethod
    def parse_exec(comp: List[CodeBlock]) -> str:
        return "\n\n".join([e.code for e in comp])

    @staticmethod
    def parse_output(output: List[CodeBlock]) -> List[IO]:
        tests: List[IO] = []
        for output_block in output:
            lines = output_block.code.splitlines()
            args_list = shlex.split(lines[0].strip("$").strip())

            command = Command(args_list[0], args_list[1], args_list[2:])
            data = "\n".join(lines[1:])
            tests.append(IO(command, data))
        return tests
