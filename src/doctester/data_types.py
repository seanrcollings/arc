from typing import List, Tuple

NO_EXECUTE = "NO_EXECUTE"
EXECUTE = "EXECUTE"
GROUP = "GROUP"


class CodeBlock:
    def __init__(self, meta: str, code: str):
        if meta == "":
            self.directive = NO_EXECUTE
            self.lang = None
        else:
            split = meta.split(" ")
            if len(split) == 2:
                directive = split[1]
                if directive == "x":
                    self.directive = NO_EXECUTE
                elif directive.isnumeric():
                    self.directive = GROUP
            else:
                self.directive = EXECUTE

            self.lang = split[0]

        self.code = code

    def __str__(self):
        return (
            f"Directive: {self.lang} : {self.directive}\n"
            "------------------\n"
            f"{self.code}\n"
            "------------------\n"
        )


class Executable:
    def __init__(self, exec_components: List[CodeBlock], output: CodeBlock = None):
        self.exec_components = exec_components
        self.output = output

    @staticmethod
    def parse_exec(ex: List[CodeBlock]) -> str:
        pass

    @staticmethod
    def parse_output(output: CodeBlock) -> Tuple[str, str]:
        pass
