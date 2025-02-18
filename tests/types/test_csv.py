from typing import Annotated
import pytest
import os
import csv

import arc
import arc.types


data = [
    ["header1", "header2", "header3"],
    ["row1_col1", "row1_col2", "row1_col3"],
    ["row2_col1", "row2_col2", "row2_col3"],
]


@pytest.fixture
def temp_csv_dir(tmpdir):
    csv_dir = tmpdir.mkdir("csv_files")
    return csv_dir


@pytest.fixture
def csv_file(temp_csv_dir):
    file_path = os.path.join(temp_csv_dir, "sample.csv")
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)
    return file_path


@pytest.fixture
def psv_file(temp_csv_dir):
    file_path = os.path.join(temp_csv_dir, "sample.psv")
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter="|")
        writer.writerows(data)
    return file_path


class TestCSVReader:
    def test_csv_reader(self, csv_file: str):
        @arc.command
        def command(csv: arc.types.CSVReader):
            return [line for line in csv]

        result = command(csv_file)
        assert result == data

    def test_psv_reader(self, psv_file: str):
        @arc.command
        def command(
            csv: Annotated[arc.types.CSVReader, arc.types.CSVReader.Args(delimiter="|")]
        ):
            return [line for line in csv]

        result = command(psv_file)
        assert result == data


class TestCSVWriter:
    def test_csv_writer(self, temp_csv_dir):
        file_path = os.path.join(temp_csv_dir, "output.csv")

        @arc.command
        def command(csv: arc.types.CSVWriter):
            csv.writerow(["header1", "header2", "header3"])
            csv.writerow(["row1_col1", "row1_col2", "row1_col3"])
            csv.writerow(["row2_col1", "row2_col2", "row2_col3"])

        command(file_path)

        with open(file_path, mode="r") as file:
            reader = csv.reader(file)
            assert [line for line in reader] == data

    def test_psv_writer(self, temp_csv_dir):
        file_path = os.path.join(temp_csv_dir, "output.psv")

        @arc.command
        def command(
            csv: Annotated[arc.types.CSVWriter, arc.types.CSVWriter.Args(delimiter="|")]
        ):
            csv.writerow(["header1", "header2", "header3"])
            csv.writerow(["row1_col1", "row1_col2", "row1_col3"])
            csv.writerow(["row2_col1", "row2_col2", "row2_col3"])

        command(file_path)

        with open(file_path, mode="r") as file:
            reader = csv.reader(file, delimiter="|")
            assert [line for line in reader] == data
