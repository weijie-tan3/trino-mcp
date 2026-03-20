"""Tests for trino_mcp.utils module."""

import pytest

from trino_mcp.utils import is_read_only_query


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM t",
        "SELECT 1",
        "SHOW TABLES",
        "SHOW SCHEMAS",
        "SHOW CATALOGS",
        "DESCRIBE my_table",
        "EXPLAIN SELECT * FROM t",
    ],
)
def test_is_read_only_query_allows_read(query):
    assert is_read_only_query(query) is True


@pytest.mark.parametrize(
    "query",
    [
        "INSERT INTO table VALUES (1)",
        "UPDATE table SET col=1",
        "DELETE FROM table",
        "CREATE TABLE test (id INT)",
        "DROP TABLE test",
        "ALTER TABLE test ADD COLUMN name VARCHAR",
        "TRUNCATE TABLE test",
        "MERGE INTO table1 USING table2 ON table1.id = table2.id",
        "WITH cte AS (DELETE FROM table RETURNING *) SELECT * FROM cte",
        "GRANT SELECT ON table TO user1",
        "REVOKE SELECT ON table FROM user1",
    ],
)
def test_is_read_only_query_blocks_write(query):
    assert is_read_only_query(query) is False


def test_is_read_only_query_blocks_explain_analyze():
    assert is_read_only_query("EXPLAIN ANALYZE SELECT * FROM t") is False


def test_is_read_only_query_unknown_command_blocked():
    """CALL is a command that may have side effects."""
    assert is_read_only_query("CALL system.sync_partition_metadata('cat','sch','tbl')") is False


def test_is_read_only_query_parse_failure():
    assert is_read_only_query("THIS IS NOT VALID SQL @@@ !!!") is False


def test_is_read_only_query_importable_from_package():
    """Verify the function is exported at the package level."""
    from trino_mcp import is_read_only_query as pkg_func

    assert pkg_func("SELECT 1") is True
