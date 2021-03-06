# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import print_function
from __future__ import unicode_literals

from click.testing import CliRunner
from pytablereader import (
    TableData,
    SqliteFileLoader,
)
import pytest
from simplesqlite import SimpleSQLite
from sqlitebiter._enum import ExitCode
from sqlitebiter.sqlitebiter import cmd


TEST_TABLE_NAME_A = "test_table_a"
TEST_TABLE_NAME_B = "test_table_b"


@pytest.fixture
def con_a0():
    con = SimpleSQLite("tmp.sqlite", "w")
    con.create_table_from_data_matrix(
        table_name=TEST_TABLE_NAME_A,
        attr_name_list=["attr_a", "attr_b"],
        data_matrix=[
            [1, 2],
            [3, 4],
        ])

    return con


@pytest.fixture
def con_a1():
    con = SimpleSQLite("tmp_dup.sqlite", "w")
    con.create_table_from_data_matrix(
        table_name=TEST_TABLE_NAME_A,
        attr_name_list=["attr_a", "attr_b"],
        data_matrix=[
            [11, 12],
            [13, 14],
        ])

    return con


@pytest.fixture
def con_b0():
    con = SimpleSQLite("tmp.sqlite", "w")
    con.create_table_from_data_matrix(
        table_name=TEST_TABLE_NAME_B,
        attr_name_list=["ba", "bb"],
        data_matrix=[
            [101, 102],
            [103, 104],
        ])

    return con


class Test_sqlitebiter_file_sqlite_merge:

    def test_normal_same_table(self, con_a0, con_a1):
        out_db_path = "test.sqlite"
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cmd,
                [
                    "file", con_a0.database_path, con_a1.database_path,
                    "-o", out_db_path,
                ])
            assert result.exit_code == ExitCode.SUCCESS

            expected = TableData(
                table_name=TEST_TABLE_NAME_A,
                header_list=["attra", "attrb"],
                record_list=[
                    [1, 2],
                    [3, 4],
                    [11, 12],
                    [13, 14],
                ])
            for tabledata in SqliteFileLoader(out_db_path).load():
                assert tabledata == expected

    def test_normal_multi_table(self, con_a0, con_b0):
        out_db_path = "test.sqlite"
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cmd,
                [
                    "file", con_a0.database_path, con_b0.database_path,
                    "-o", out_db_path,
                ])
            assert result.exit_code == ExitCode.SUCCESS

            expected_list = [
                TableData(
                    table_name=TEST_TABLE_NAME_A,
                    header_list=["attra", "attrb"],
                    record_list=[
                        [1, 2],
                        [3, 4],
                    ]),
                TableData(
                    table_name=TEST_TABLE_NAME_B,
                    header_list=["ba", "bb"],
                    record_list=[
                        [101, 102],
                        [103, 104],
                    ]),
            ]
            for tabledata in SqliteFileLoader(out_db_path).load():
                print("[actual]   {}".format(tabledata))

                assert tabledata in expected_list
