import os
import re
from typing import List
from .data_types import (
    CodeBlock,
    Executable,
    OUTPUT,
)


def walk_dir(directory):
    parsed_files: List[List[CodeBlock]] = []
    for root, _, files in os.walk(directory, topdown=True):
        for file in files:
            parsed_files.append(parse_file(f"{root}/{file}"))
    return parsed_files


def parse_file(file_name):
    regex = r"```([a-wyz0-9 ]+)\n([\s\S]*?)\n```"
    blocks = []
    with open(file_name) as file:
        test_str = file.read()
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for match in matches:
            blocks.append(
                CodeBlock(match.group(1), match.group(2), file_name=file_name)
            )
    return blocks


def make_groups(blocks) -> List[List[CodeBlock]]:
    groups: List[List[CodeBlock]] = []
    while len(blocks) > 0:
        first_block = blocks.pop(0)
        group: List[CodeBlock] = [first_block]
        for _ in range(0, len(blocks) - 1):
            block = blocks[0]
            if (
                block.lang == first_block.lang
                and block.fragment_index > first_block.fragment_index
            ):
                group.append(blocks.pop(0))
            else:
                break
        groups.append(group)
    return groups


def execute_factory(blocks: List[CodeBlock]) -> List[Executable]:
    executables: List[Executable] = []
    groups = make_groups(blocks)

    for index, group in enumerate(groups):
        group_type = group[0].type
        if group_type == OUTPUT:
            continue

        output_group = []
        if index + 1 < len(groups) - 1 and groups[index + 1][0].type == OUTPUT:
            output_group = groups[index + 1]

        executables.append(Executable(group, output_group))
    return executables


def get_executables(root_dir: str):
    parsed_files = walk_dir(root_dir)
    executables = []
    for p in parsed_files:
        executables += execute_factory(p)
    return executables


def test_docs_dir(root_dir: str):
    executables = get_executables(root_dir)
    for exe in executables:
        exe.execute()


# def test_doc_file(file_name: str):
#     parsed_file = parse_file(file_name)
#     executable = execute_factory(parsed_file)
#     for exe in executable:
#         exe.test_execute()
