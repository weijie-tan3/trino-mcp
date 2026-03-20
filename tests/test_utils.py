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
        "INSERT INTO t VALUES (1)",
        "UPDATE t SET col=1",
        "DELETE FROM t",
        "CREATE TABLE t (id INT)",
        "DROP TABLE t",
        "ALTER TABLE t ADD COLUMN name VARCHAR",
        "TRUNCATE TABLE t",
        "MERGE INTO t1 USING t2 ON t1.id = t2.id",
    ],
)
def test_is_read_only_query_blocks_write(query):
    assert is_read_only_query(query) is False


def test_is_read_only_query_blocks_explain_analyze():
    assert is_read_only_query("EXPLAIN ANALYZE SELECT * FROM t") is False


def test_is_read_only_query_parse_failure():
    assert is_read_only_query("THIS IS NOT VALID SQL @@@ !!!") is False


def test_is_read_only_query_importable_from_package():
    """Verify the function is exported at the package level."""
    from trino_mcp import is_read_only_query as pkg_func

    assert pkg_func("SELECT 1") is True
