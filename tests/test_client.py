"""Tests for Trino client module."""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from trino_mcp.client import TrinoClient
from trino_mcp.config import TrinoConfig


@pytest.fixture
def config():
    """Create a test configuration."""
    return TrinoConfig(
        host="localhost",
        port=8080,
        user="trino",
        catalog="test_catalog",
        schema="test_schema",
        allow_write_queries=True,  # Enable for backward compatibility with existing tests
    )


@pytest.fixture
def mock_connection():
    """Create a mock Trino connection."""
    with patch("trino_mcp.client.trino.dbapi.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn


def test_client_initialization(config, mock_connection):
    """Test client initialization."""
    client = TrinoClient(config)

    assert client.config == config
    assert client.connection == mock_connection


def test_execute_query_with_results(config, mock_connection):
    """Test executing a query that returns results."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("col1",), ("col2",)]
    mock_cursor.fetchall.return_value = [("val1", "val2"), ("val3", "val4")]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.execute_query("SELECT * FROM test")

    data = json.loads(result)
    assert len(data) == 2
    assert data[0] == {"col1": "val1", "col2": "val2"}
    assert data[1] == {"col1": "val3", "col2": "val4"}


def test_execute_query_without_results(config, mock_connection):
    """Test executing a query without results (DDL/DML)."""
    mock_cursor = MagicMock()
    mock_cursor.description = None
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.execute_query("CREATE TABLE test (id INT)")

    data = json.loads(result)
    assert data["status"] == "success"
    assert "executed successfully" in data["message"]


def test_list_catalogs(config, mock_connection):
    """Test listing catalogs."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Catalog",)]
    mock_cursor.fetchall.return_value = [("catalog1",), ("catalog2",), ("catalog3",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    catalogs = client.list_catalogs()

    assert catalogs == ["catalog1", "catalog2", "catalog3"]


def test_list_schemas(config, mock_connection):
    """Test listing schemas."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Schema",)]
    mock_cursor.fetchall.return_value = [("schema1",), ("schema2",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    schemas = client.list_schemas("test_catalog")

    assert schemas == ["schema1", "schema2"]
    mock_cursor.execute.assert_called_with("SHOW SCHEMAS FROM test_catalog")


def test_list_schemas_with_default(config, mock_connection):
    """Test listing schemas using default catalog."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Schema",)]
    mock_cursor.fetchall.return_value = [("schema1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    schemas = client.list_schemas("")

    assert schemas == ["schema1"]
    mock_cursor.execute.assert_called_with("SHOW SCHEMAS FROM test_catalog")


def test_list_schemas_no_catalog_error(mock_connection):
    """Test listing schemas without catalog raises error."""
    config = TrinoConfig(host="localhost", port=8080, user="trino")
    client = TrinoClient(config)

    with pytest.raises(ValueError, match="Catalog must be specified"):
        client.list_schemas("")


def test_list_tables(config, mock_connection):
    """Test listing tables."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Table",)]
    mock_cursor.fetchall.return_value = [("table1",), ("table2",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    tables = client.list_tables("catalog1", "schema1")

    assert tables == ["table1", "table2"]
    mock_cursor.execute.assert_called_with("SHOW TABLES FROM catalog1.schema1")


def test_list_tables_with_defaults(config, mock_connection):
    """Test listing tables using default catalog and schema."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Table",)]
    mock_cursor.fetchall.return_value = [("table1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    tables = client.list_tables("", "")

    assert tables == ["table1"]
    mock_cursor.execute.assert_called_with("SHOW TABLES FROM test_catalog.test_schema")


def test_list_tables_missing_catalog_error(mock_connection):
    """Test listing tables without catalog raises error."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", schema="test_schema"
    )
    client = TrinoClient(config)

    with pytest.raises(ValueError, match="Both catalog and schema must be specified"):
        client.list_tables("", "")


def test_describe_table(config, mock_connection):
    """Test describing a table."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Column",), ("Type",)]
    mock_cursor.fetchall.return_value = [("id", "integer"), ("name", "varchar")]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.describe_table("catalog1", "schema1", "table1")

    data = json.loads(result)
    assert len(data) == 2
    mock_cursor.execute.assert_called_with("DESCRIBE catalog1.schema1.table1")


def test_show_create_table(config, mock_connection):
    """Test showing CREATE TABLE statement."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Create Table",)]
    mock_cursor.fetchall.return_value = [("CREATE TABLE test (id INT)",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.show_create_table("catalog1", "schema1", "table1")

    assert result == "CREATE TABLE test (id INT)"
    mock_cursor.execute.assert_called_with("SHOW CREATE TABLE catalog1.schema1.table1")


def test_get_table_stats(config, mock_connection):
    """Test getting table statistics."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("column_name",), ("data_size",)]
    mock_cursor.fetchall.return_value = [("col1", "100"), ("col2", "200")]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.get_table_stats("catalog1", "schema1", "table1")

    data = json.loads(result)
    assert len(data) == 2
    mock_cursor.execute.assert_called_with("SHOW STATS FOR catalog1.schema1.table1")


# Tests for query permission feature
def test_is_write_query_insert(config, mock_connection):
    """Test detection of INSERT query."""
    client = TrinoClient(config)
    assert client._is_write_query("INSERT INTO table VALUES (1, 2)")
    assert client._is_write_query("insert into table values (1, 2)")
    assert client._is_write_query("  INSERT  INTO table VALUES (1, 2)  ")


def test_is_write_query_update(config, mock_connection):
    """Test detection of UPDATE query."""
    client = TrinoClient(config)
    assert client._is_write_query("UPDATE table SET col = 1")
    assert client._is_write_query("update table set col = 1")


def test_is_write_query_delete(config, mock_connection):
    """Test detection of DELETE query."""
    client = TrinoClient(config)
    assert client._is_write_query("DELETE FROM table WHERE id = 1")
    assert client._is_write_query("delete from table")


def test_is_write_query_create(config, mock_connection):
    """Test detection of CREATE query."""
    client = TrinoClient(config)
    assert client._is_write_query("CREATE TABLE test (id INT)")
    assert client._is_write_query("create table test (id int)")
    assert client._is_write_query("CREATE OR REPLACE TABLE test (id INT)")


def test_is_write_query_drop(config, mock_connection):
    """Test detection of DROP query."""
    client = TrinoClient(config)
    assert client._is_write_query("DROP TABLE test")
    assert client._is_write_query("drop table test")


def test_is_write_query_alter(config, mock_connection):
    """Test detection of ALTER query."""
    client = TrinoClient(config)
    assert client._is_write_query("ALTER TABLE test ADD COLUMN col INT")
    assert client._is_write_query("alter table test drop column col")


def test_is_write_query_truncate(config, mock_connection):
    """Test detection of TRUNCATE query."""
    client = TrinoClient(config)
    assert client._is_write_query("TRUNCATE TABLE test")
    assert client._is_write_query("truncate table test")


def test_is_write_query_merge(config, mock_connection):
    """Test detection of MERGE query."""
    client = TrinoClient(config)
    assert client._is_write_query("MERGE INTO target USING source ON target.id = source.id")


def test_is_write_query_with_comments(config, mock_connection):
    """Test detection of write query with comments."""
    client = TrinoClient(config)
    assert client._is_write_query("-- This is a comment\nINSERT INTO table VALUES (1)")
    assert client._is_write_query("/* Multi-line\n comment */ DELETE FROM table")


def test_is_read_query_select(config, mock_connection):
    """Test that SELECT queries are not flagged as write queries."""
    client = TrinoClient(config)
    assert not client._is_write_query("SELECT * FROM table")
    assert not client._is_write_query("select * from table")
    assert not client._is_write_query("SELECT col FROM table WHERE id = 1")


def test_is_read_query_show(config, mock_connection):
    """Test that SHOW queries are not flagged as write queries."""
    client = TrinoClient(config)
    assert not client._is_write_query("SHOW TABLES")
    assert not client._is_write_query("SHOW SCHEMAS FROM catalog")
    assert not client._is_write_query("SHOW CREATE TABLE test")


def test_is_read_query_describe(config, mock_connection):
    """Test that DESCRIBE queries are not flagged as write queries."""
    client = TrinoClient(config)
    assert not client._is_write_query("DESCRIBE table")
    assert not client._is_write_query("describe table")


def test_is_read_query_explain(config, mock_connection):
    """Test that EXPLAIN queries are not flagged as write queries."""
    client = TrinoClient(config)
    assert not client._is_write_query("EXPLAIN SELECT * FROM table")
    assert not client._is_write_query("EXPLAIN ANALYZE SELECT * FROM table")


def test_execute_query_write_disabled_blocks_insert(mock_connection):
    """Test that INSERT is blocked when write queries are disabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=False
    )
    client = TrinoClient(config)

    with pytest.raises(PermissionError, match="Write queries are disabled"):
        client.execute_query("INSERT INTO table VALUES (1, 2)")


def test_execute_query_write_disabled_blocks_update(mock_connection):
    """Test that UPDATE is blocked when write queries are disabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=False
    )
    client = TrinoClient(config)

    with pytest.raises(PermissionError, match="Write queries are disabled"):
        client.execute_query("UPDATE table SET col = 1")


def test_execute_query_write_disabled_blocks_delete(mock_connection):
    """Test that DELETE is blocked when write queries are disabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=False
    )
    client = TrinoClient(config)

    with pytest.raises(PermissionError, match="Write queries are disabled"):
        client.execute_query("DELETE FROM table WHERE id = 1")


def test_execute_query_write_disabled_blocks_create(mock_connection):
    """Test that CREATE is blocked when write queries are disabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=False
    )
    client = TrinoClient(config)

    with pytest.raises(PermissionError, match="Write queries are disabled"):
        client.execute_query("CREATE TABLE test (id INT)")


def test_execute_query_write_disabled_blocks_drop(mock_connection):
    """Test that DROP is blocked when write queries are disabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=False
    )
    client = TrinoClient(config)

    with pytest.raises(PermissionError, match="Write queries are disabled"):
        client.execute_query("DROP TABLE test")


def test_execute_query_write_disabled_allows_select(mock_connection):
    """Test that SELECT is allowed when write queries are disabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=False
    )
    mock_cursor = MagicMock()
    mock_cursor.description = [("col1",)]
    mock_cursor.fetchall.return_value = [("val1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.execute_query("SELECT * FROM table")

    data = json.loads(result)
    assert len(data) == 1
    assert data[0] == {"col1": "val1"}


def test_execute_query_write_enabled_allows_insert(mock_connection):
    """Test that INSERT is allowed when write queries are enabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=True
    )
    mock_cursor = MagicMock()
    mock_cursor.description = None
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.execute_query("INSERT INTO table VALUES (1, 2)")

    data = json.loads(result)
    assert data["status"] == "success"


def test_execute_query_write_enabled_allows_create(mock_connection):
    """Test that CREATE is allowed when write queries are enabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=True
    )
    mock_cursor = MagicMock()
    mock_cursor.description = None
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.execute_query("CREATE TABLE test (id INT)")

    data = json.loads(result)
    assert data["status"] == "success"


def test_execute_query_write_enabled_allows_select(mock_connection):
    """Test that SELECT is allowed when write queries are enabled."""
    config = TrinoConfig(
        host="localhost", port=8080, user="trino", allow_write_queries=True
    )
    mock_cursor = MagicMock()
    mock_cursor.description = [("col1",)]
    mock_cursor.fetchall.return_value = [("val1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.execute_query("SELECT * FROM table")

    data = json.loads(result)
    assert len(data) == 1
    assert data[0] == {"col1": "val1"}

