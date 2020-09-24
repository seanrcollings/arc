import re
from typing import List
from doctester.data_types import CodeBlock, Executable, GROUP, NO_EXECUTE, EXECUTE

# def walk_dir(directory):
#     for root, dirs, files in os.walk(directory, topdown=True):
#         for file in files:
#             parse_file(f"{root}/{file}")


def parse_file(file_name):
    regex = r"```([a-z0-9 ]*)\n([\s\S]*?)\n```"
    blocks = []
    with open(file_name) as file:
        test_str = file.read()
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for match in matches:
            blocks.append(CodeBlock(match.group(1), match.group(2)))
    return blocks


def execute_factory(blocks: List[CodeBlock]) -> List[Executable]:
    executables: List[Executable] = []
    breakpoint()
    while len(blocks) != 0:
        block = blocks.pop(0)

        if block.directive == GROUP:
            group = [block]

            for group_block in blocks:
                # breakpoint()
                if group_block.directive != GROUP:
                    break
                group.append(blocks.pop(0))

            output = None
            if len(blocks) != 0 and blocks[0].lang == "out":
                output = blocks.pop(0)
            executables.append(Executable(group, output))

        elif block.directive == EXECUTE:
            output = None
            if len(blocks) != 0 and blocks[0].lang == "out":
                output = blocks.pop(0)
            executables.append(Executable([block], output))

    return executables


b = parse_file("docs/test.md")
d = execute_factory(b)
for ex in d:
    print("----------------")
    for comp in ex.exec_components:
        print(comp.code)
    print("----------------")
