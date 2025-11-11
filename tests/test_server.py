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
def test_execute_query_tool(mock_client):
    """Test execute_query tool."""
    from trino_mcp.server import execute_query

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
