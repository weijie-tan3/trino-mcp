"""Tests for MCP server module."""

import os
from unittest.mock import MagicMock, patch

import pytest


# Set environment variables before importing server module
@pytest.fixture(scope="module", autouse=True)
def setup_env():
    """Setup environment variables for all tests."""
    os.environ["AUTH_METHOD"] = "NONE"
    os.environ["TRINO_HOST"] = "localhost"
    os.environ["TRINO_PORT"] = "8080"
    os.environ["TRINO_USER"] = "trino"
    yield
    # Cleanup
    for key in ["AUTH_METHOD", "TRINO_HOST", "TRINO_PORT", "TRINO_USER"]:
        os.environ.pop(key, None)


@patch("trino_mcp.server.client")
def test_list_catalogs_tool(mock_client):
    """Test list_catalogs tool."""
    from trino_mcp.server import list_catalogs

    mock_client.list_catalogs.return_value = ["catalog1", "catalog2"]

    result = list_catalogs()

    assert result == "catalog1\ncatalog2"
    mock_client.list_catalogs.assert_called_once()


@patch("trino_mcp.server.client")
def test_list_catalogs_error(mock_client):
    """Test list_catalogs tool with error."""
    from trino_mcp.server import list_catalogs

    mock_client.list_catalogs.side_effect = Exception("Connection failed")

    result = list_catalogs()

    assert "Error listing catalogs" in result
    assert "Connection failed" in result


@patch("trino_mcp.server.client")
def test_list_schemas_tool(mock_client):
    """Test list_schemas tool."""
    from trino_mcp.server import list_schemas

    mock_client.list_schemas.return_value = ["schema1", "schema2"]

    result = list_schemas("test_catalog")

    assert result == "schema1\nschema2"
    mock_client.list_schemas.assert_called_once_with("test_catalog")


@patch("trino_mcp.server.client")
def test_list_tables_tool(mock_client):
    """Test list_tables tool."""
    from trino_mcp.server import list_tables

    mock_client.list_tables.return_value = ["table1", "table2"]

    result = list_tables("catalog1", "schema1")

    assert result == "table1\ntable2"
    mock_client.list_tables.assert_called_once_with("catalog1", "schema1")


@patch("trino_mcp.server.client")
def test_describe_table_tool(mock_client):
    """Test describe_table tool."""
    from trino_mcp.server import describe_table

    mock_client.describe_table.return_value = '{"column": "id", "type": "integer"}'

    result = describe_table("table1", "catalog1", "schema1")

    assert "id" in result
    mock_client.describe_table.assert_called_once_with("catalog1", "schema1", "table1")


@patch("trino_mcp.server.client")
def test_execute_query_read_only_tool(mock_client):
    """Test execute_query_read_only tool with SELECT query."""
    from trino_mcp.server import execute_query_read_only

    mock_client.execute_query.return_value = '[{"col": "value"}]'

    result = execute_query_read_only("SELECT 1")

    assert "value" in result
    mock_client.execute_query.assert_called_once_with("SELECT 1")


@patch("trino_mcp.server.client")
def test_execute_query_read_only_blocks_insert(mock_client):
    """Test execute_query_read_only tool blocks INSERT queries."""
    from trino_mcp.server import execute_query_read_only

    result = execute_query_read_only("INSERT INTO table VALUES (1)")

    assert "does not appear to be read-only" in result
    assert "execute_query" in result
    # Client should not be called for non-read-only queries
    mock_client.execute_query.assert_not_called()


@patch("trino_mcp.server.client")
def test_execute_query_read_only_blocks_update(mock_client):
    """Test execute_query_read_only tool blocks UPDATE queries."""
    from trino_mcp.server import execute_query_read_only

    result = execute_query_read_only("UPDATE table SET col=1")

    assert "does not appear to be read-only" in result
    mock_client.execute_query.assert_not_called()


@patch("trino_mcp.server.client")
def test_execute_query_read_only_blocks_delete(mock_client):
    """Test execute_query_read_only tool blocks DELETE queries."""
    from trino_mcp.server import execute_query_read_only

    result = execute_query_read_only("DELETE FROM table")

    assert "does not appear to be read-only" in result
    mock_client.execute_query.assert_not_called()


@patch("trino_mcp.server.client")
def test_execute_query_read_only_blocks_create(mock_client):
    """Test execute_query_read_only tool blocks CREATE queries."""
    from trino_mcp.server import execute_query_read_only

    result = execute_query_read_only("CREATE TABLE test (id INT)")

    assert "does not appear to be read-only" in result
    mock_client.execute_query.assert_not_called()


@patch("trino_mcp.server.client")
def test_execute_query_read_only_blocks_drop(mock_client):
    """Test execute_query_read_only tool blocks DROP queries."""
    from trino_mcp.server import execute_query_read_only

    result = execute_query_read_only("DROP TABLE test")

    assert "does not appear to be read-only" in result
    mock_client.execute_query.assert_not_called()


@patch("trino_mcp.server.client")
def test_execute_query_read_only_allows_show(mock_client):
    """Test execute_query_read_only tool allows SHOW queries."""
    from trino_mcp.server import execute_query_read_only

    mock_client.execute_query.return_value = '[{"table": "test"}]'

    result = execute_query_read_only("SHOW TABLES")

    assert "test" in result
    mock_client.execute_query.assert_called_once_with("SHOW TABLES")


@patch("trino_mcp.server.client")
def test_execute_query_read_only_allows_describe(mock_client):
    """Test execute_query_read_only tool allows DESCRIBE queries."""
    from trino_mcp.server import execute_query_read_only

    mock_client.execute_query.return_value = '[{"column": "id"}]'

    result = execute_query_read_only("DESCRIBE table")

    assert "id" in result
    mock_client.execute_query.assert_called_once_with("DESCRIBE table")


@patch("trino_mcp.server.client")
def test_execute_query_read_only_allows_explain(mock_client):
    """Test execute_query_read_only tool allows EXPLAIN queries."""
    from trino_mcp.server import execute_query_read_only

    mock_client.execute_query.return_value = '[{"plan": "..."}]'

    result = execute_query_read_only("EXPLAIN SELECT * FROM table")

    assert "plan" in result
    mock_client.execute_query.assert_called_once()


@patch("trino_mcp.server.client")
@patch("trino_mcp.server.config")
def test_execute_query_tool_write_disabled(mock_config, mock_client):
    """Test execute_query tool with write queries disabled."""
    from trino_mcp.server import execute_query

    mock_config.allow_write_queries = False

    result = execute_query("INSERT INTO table VALUES (1)")

    assert "Write queries are disabled" in result
    assert "ALLOW_WRITE_QUERIES=true" in result
    assert "execute_query_read_only" in result
    # Client should not be called when write queries are disabled
    mock_client.execute_query.assert_not_called()


@patch("trino_mcp.server.client")
@patch("trino_mcp.server.config")
def test_execute_query_tool_write_enabled(mock_config, mock_client):
    """Test execute_query tool with write queries enabled."""
    from trino_mcp.server import execute_query

    mock_config.allow_write_queries = True
    mock_client.execute_query.return_value = '[{"col": "value"}]'

    result = execute_query("SELECT 1")

    assert "value" in result
    mock_client.execute_query.assert_called_once_with("SELECT 1")


@patch("trino_mcp.server.client")
def test_show_create_table_tool(mock_client):
    """Test show_create_table tool."""
    from trino_mcp.server import show_create_table

    mock_client.show_create_table.return_value = "CREATE TABLE test (id INT)"

    result = show_create_table("table1", "catalog1", "schema1")

    assert "CREATE TABLE" in result
    mock_client.show_create_table.assert_called_once_with(
        "catalog1", "schema1", "table1"
    )


@patch("trino_mcp.server.client")
def test_get_table_stats_tool(mock_client):
    """Test get_table_stats tool."""
    from trino_mcp.server import get_table_stats

    mock_client.get_table_stats.return_value = '[{"column": "id", "size": "100"}]'

    result = get_table_stats("table1", "catalog1", "schema1")

    assert "100" in result
    mock_client.get_table_stats.assert_called_once_with("catalog1", "schema1", "table1")


def test_mcp_server_initialization():
    """Test MCP server is properly initialized."""
    from trino_mcp.server import mcp

    assert mcp is not None
    assert mcp.name == "Trino MCP Server"


def test_main_function_exists():
    """Test main function exists."""
    from trino_mcp.server import main

    assert callable(main)
