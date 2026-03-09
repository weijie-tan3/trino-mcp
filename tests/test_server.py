"""Tests for MCP server module."""

import asyncio
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

    result = asyncio.run(list_catalogs())

    assert result == "catalog1\ncatalog2"
    mock_client.list_catalogs.assert_called_once()


@patch("trino_mcp.server.client")
def test_list_catalogs_error(mock_client):
    """Test list_catalogs tool with error."""
    from trino_mcp.server import list_catalogs

    mock_client.list_catalogs.side_effect = Exception("Connection failed")

    result = asyncio.run(list_catalogs())

    assert "Error listing catalogs" in result
    assert "Connection failed" in result


@patch("trino_mcp.server.client")
def test_list_schemas_tool(mock_client):
    """Test list_schemas tool."""
    from trino_mcp.server import list_schemas

    mock_client.list_schemas.return_value = ["schema1", "schema2"]

    result = asyncio.run(list_schemas("test_catalog"))

    assert result == "schema1\nschema2"
    mock_client.list_schemas.assert_called_once_with("test_catalog")


@patch("trino_mcp.server.client")
def test_list_tables_tool(mock_client):
    """Test list_tables tool."""
    from trino_mcp.server import list_tables

    mock_client.list_tables.return_value = ["table1", "table2"]

    result = asyncio.run(list_tables("catalog1", "schema1"))

    assert result == "table1\ntable2"
    mock_client.list_tables.assert_called_once_with("catalog1", "schema1")


@patch("trino_mcp.server.client")
def test_describe_table_tool(mock_client):
    """Test describe_table tool."""
    from trino_mcp.server import describe_table

    mock_client.describe_table.return_value = '{"column": "id", "type": "integer"}'

    result = asyncio.run(describe_table("table1", "catalog1", "schema1"))

    assert "id" in result
    mock_client.describe_table.assert_called_once_with("catalog1", "schema1", "table1")


@patch("trino_mcp.server.client")
def test_execute_query_read_only_tool(mock_client):
    """Test execute_query_read_only tool with SELECT query."""
    from trino_mcp.server import execute_query_read_only

    mock_client.execute_query_json.return_value = '[{"col": "value"}]'

    result = asyncio.run(execute_query_read_only("SELECT 1"))

    assert "value" in result
    mock_client.execute_query_json.assert_called_once_with("SELECT 1")


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
        "WITH cte AS (DELETE FROM table RETURNING *) SELECT * FROM cte"
    ],
)
@patch("trino_mcp.server.client")
def test_execute_query_read_only_blocks_write_queries(mock_client, query):
    """Test execute_query_read_only tool blocks non-read-only queries."""
    from trino_mcp.server import execute_query_read_only, _is_read_only_query

    assert not _is_read_only_query(query)

    result = asyncio.run(execute_query_read_only(query))

    assert "does not appear to be read-only" in result
    assert "execute_query" in result
    # Client should not be called for non-read-only queries
    mock_client.execute_query_json.assert_not_called()


@pytest.mark.parametrize(
    "query,expected_content",
    [
        ("SHOW TABLES", "table"),
        ("DESCRIBE my_table", "column"),
        ("EXPLAIN SELECT * FROM table", "plan"),
        ("SHOW SCHEMAS", "schema"),
        ("SHOW CATALOGS", "catalog"),
    ],
)
@patch("trino_mcp.server.client")
def test_execute_query_read_only_allows_read_queries(mock_client, query, expected_content):
    """Test execute_query_read_only tool allows read-only queries."""
    from trino_mcp.server import execute_query_read_only, _is_read_only_query

    assert _is_read_only_query(query)

    mock_client.execute_query_json.return_value = f'[{{"{expected_content}": "test"}}]'

    result = asyncio.run(execute_query_read_only(query))

    assert "test" in result
    mock_client.execute_query_json.assert_called_once_with(query)


@patch("trino_mcp.server.client")
@patch("trino_mcp.server.config")
def test_execute_query_tool_write_disabled(mock_config, mock_client):
    """Test execute_query tool with write queries disabled."""
    from trino_mcp.server import execute_query

    mock_config.allow_write_queries = False

    result = asyncio.run(execute_query("INSERT INTO table VALUES (1)"))

    assert "Write queries are disabled" in result
    assert "ALLOW_WRITE_QUERIES=true" in result
    assert "execute_query_read_only" in result
    # Client should not be called when write queries are disabled
    mock_client.execute_query_json.assert_not_called()


@patch("trino_mcp.server.client")
@patch("trino_mcp.server.config")
def test_execute_query_tool_write_enabled(mock_config, mock_client):
    """Test execute_query tool with write queries enabled."""
    from trino_mcp.server import execute_query

    mock_config.allow_write_queries = True
    mock_client.execute_query_json.return_value = '[{"col": "value"}]'

    result = asyncio.run(execute_query("SELECT 1"))

    assert "value" in result
    mock_client.execute_query_json.assert_called_once_with("SELECT 1")


@patch("trino_mcp.server.client")
def test_show_create_table_tool(mock_client):
    """Test show_create_table tool."""
    from trino_mcp.server import show_create_table

    mock_client.show_create_table.return_value = "CREATE TABLE test (id INT)"

    result = asyncio.run(show_create_table("table1", "catalog1", "schema1"))

    assert "CREATE TABLE" in result
    mock_client.show_create_table.assert_called_once_with(
        "catalog1", "schema1", "table1"
    )


@patch("trino_mcp.server.client")
def test_get_table_stats_tool(mock_client):
    """Test get_table_stats tool."""
    from trino_mcp.server import get_table_stats

    mock_client.get_table_stats.return_value = '[{"column": "id", "size": "100"}]'

    result = asyncio.run(get_table_stats("table1", "catalog1", "schema1"))

    assert "100" in result
    mock_client.get_table_stats.assert_called_once_with("catalog1", "schema1", "table1")


def test_mcp_server_initialization():
    """Test MCP server is properly initialized."""
    from trino_mcp.server import mcp

    assert mcp is not None
    assert mcp.name == "Trino MCP Server"


@patch("trino_mcp.server.client")
def test_execute_query_read_only_output_file_csv(mock_client):
    """Test execute_query_read_only with .csv output_file delegates to execute_query_to_file."""
    from trino_mcp.server import execute_query_read_only

    mock_client.execute_query_to_file.return_value = 2

    result = asyncio.run(execute_query_read_only("SELECT 1", output_file="/tmp/results.csv"))

    assert "results.csv" in result
    assert "2 row(s)" in result
    mock_client.execute_query_to_file.assert_called_once_with("SELECT 1", "/tmp/results.csv")


@patch("trino_mcp.server.client")
@patch("trino_mcp.server.config")
def test_execute_query_output_file_csv(mock_config, mock_client):
    """Test execute_query with .csv output_file delegates to execute_query_to_file."""
    from trino_mcp.server import execute_query

    mock_config.allow_write_queries = True
    mock_client.execute_query_to_file.return_value = 2

    result = asyncio.run(execute_query("SELECT 1", output_file="/tmp/results.csv"))

    assert "results.csv" in result
    assert "2 row(s)" in result
    mock_client.execute_query_to_file.assert_called_once_with("SELECT 1", "/tmp/results.csv")


@patch("trino_mcp.server.client")
def test_execute_query_read_only_output_file(mock_client):
    """Test execute_query_read_only with output_file delegates to execute_query_to_file."""
    from trino_mcp.server import execute_query_read_only

    mock_client.execute_query_to_file.return_value = 5

    result = asyncio.run(execute_query_read_only("SELECT 1", output_file="/tmp/results.json"))

    assert "results.json" in result
    assert "5 row(s)" in result
    mock_client.execute_query_to_file.assert_called_once_with("SELECT 1", "/tmp/results.json")


@patch("trino_mcp.server.client")
@patch("trino_mcp.server.config")
def test_execute_query_output_file(mock_config, mock_client):
    """Test execute_query with output_file delegates to execute_query_to_file."""
    from trino_mcp.server import execute_query

    mock_config.allow_write_queries = True
    mock_client.execute_query_to_file.return_value = 5

    result = asyncio.run(execute_query("SELECT 1", output_file="/tmp/results.json"))

    assert "results.json" in result
    assert "5 row(s)" in result
    mock_client.execute_query_to_file.assert_called_once_with("SELECT 1", "/tmp/results.json")


def test_parse_table_identifier_simple():
    """Test _parse_table_identifier with a simple table name."""
    from trino_mcp.server import _parse_table_identifier

    cat, sch, tbl = _parse_table_identifier("my_table", "cat", "sch")
    assert cat == "cat"
    assert sch == "sch"
    assert tbl == "my_table"


def test_parse_table_identifier_fully_qualified():
    """Test _parse_table_identifier with a fully qualified name (catalog.schema.table)."""
    from trino_mcp.server import _parse_table_identifier

    cat, sch, tbl = _parse_table_identifier("catalog1.schema1.table1", "", "")
    assert cat == "catalog1"
    assert sch == "schema1"
    assert tbl == "table1"


def test_parse_table_identifier_fully_qualified_with_existing_catalog_schema():
    """Test _parse_table_identifier with a fully qualified name when catalog/schema are already provided."""
    from trino_mcp.server import _parse_table_identifier

    cat, sch, tbl = _parse_table_identifier("catalog1.schema1.table1", "existing_cat", "existing_sch")
    assert cat == "existing_cat"
    assert sch == "existing_sch"
    assert tbl == "table1"


def test_parse_table_identifier_schema_qualified():
    """Test _parse_table_identifier with a schema-qualified name (schema.table)."""
    from trino_mcp.server import _parse_table_identifier

    cat, sch, tbl = _parse_table_identifier("schema1.table1", "", "")
    assert cat == ""
    assert sch == "schema1"
    assert tbl == "table1"


def test_parse_table_identifier_schema_qualified_with_existing_schema():
    """Test _parse_table_identifier with a schema-qualified name when schema is already provided."""
    from trino_mcp.server import _parse_table_identifier

    cat, sch, tbl = _parse_table_identifier("schema1.table1", "cat", "existing_sch")
    assert cat == "cat"
    assert sch == "existing_sch"
    assert tbl == "table1"


@patch("trino_mcp.server.client")
def test_describe_table_with_fully_qualified_name(mock_client):
    """Test describe_table tool handles fully qualified table name."""
    from trino_mcp.server import describe_table

    mock_client.describe_table.return_value = '{"column": "id", "type": "integer"}'

    result = asyncio.run(describe_table("catalog1.schema1.table1", "", ""))

    assert "id" in result
    mock_client.describe_table.assert_called_once_with("catalog1", "schema1", "table1")


@patch("trino_mcp.server.client")
def test_show_create_table_with_fully_qualified_name(mock_client):
    """Test show_create_table tool handles fully qualified table name."""
    from trino_mcp.server import show_create_table

    mock_client.show_create_table.return_value = "CREATE TABLE test (id INT)"

    result = asyncio.run(show_create_table("catalog1.schema1.table1", "", ""))

    assert "CREATE TABLE" in result
    mock_client.show_create_table.assert_called_once_with("catalog1", "schema1", "table1")


@patch("trino_mcp.server.client")
def test_get_table_stats_with_fully_qualified_name(mock_client):
    """Test get_table_stats tool handles fully qualified table name."""
    from trino_mcp.server import get_table_stats

    mock_client.get_table_stats.return_value = '[{"column": "id", "size": "100"}]'

    result = asyncio.run(get_table_stats("catalog1.schema1.table1", "", ""))

    assert "100" in result
    mock_client.get_table_stats.assert_called_once_with("catalog1", "schema1", "table1")


def test_main_function_exists():
    """Test main function exists."""
    from trino_mcp.server import main

    assert callable(main)


# ---------------------------------------------------------------------------
# Concurrency gate tests
# ---------------------------------------------------------------------------


@patch("trino_mcp.server.client")
def test_concurrency_gate_rejects_when_locked(mock_client):
    """Test that a tool call returns rejection message when semaphore is locked."""
    from trino_mcp.server import list_catalogs, _query_semaphore, _concurrency_limit_message

    async def _test():
        # Acquire the semaphore to simulate an in-progress call
        await _query_semaphore.acquire()
        try:
            result = await list_catalogs()
            assert "concurrent query slot" in result
            assert "Please wait" in result
            # client should NOT have been called
            mock_client.list_catalogs.assert_not_called()
        finally:
            _query_semaphore.release()

    asyncio.run(_test())


@patch("trino_mcp.server.client")
def test_concurrency_gate_allows_when_free(mock_client):
    """Test that a tool call proceeds normally when the semaphore is free."""
    from trino_mcp.server import list_catalogs

    mock_client.list_catalogs.return_value = ["cat1"]

    result = asyncio.run(list_catalogs())

    assert result == "cat1"
    mock_client.list_catalogs.assert_called_once()


def test_concurrency_limit_message_content():
    """Test the rejection message includes the configured limit."""
    from trino_mcp.server import _concurrency_limit_message, config

    msg = _concurrency_limit_message()
    assert str(config.max_concurrent_queries) in msg
    assert "Please wait" in msg


# ---------------------------------------------------------------------------
# QueryTimeoutError handling in tools
# ---------------------------------------------------------------------------


@patch("trino_mcp.server.client")
def test_try_execute_query_handles_timeout(mock_client):
    """Test that _try_execute_query catches QueryTimeoutError."""
    from trino_mcp.client import QueryTimeoutError
    from trino_mcp.server import _try_execute_query

    mock_client.execute_query_json.side_effect = QueryTimeoutError(
        "Query cancelled after exceeding the 5-minute timeout."
    )

    result = _try_execute_query("SELECT slow()")

    assert "timeout" in result.lower()
    assert "Error" in result


@patch("trino_mcp.server.client")
def test_list_catalogs_handles_timeout(mock_client):
    """Test that list_catalogs handles QueryTimeoutError gracefully."""
    from trino_mcp.client import QueryTimeoutError
    from trino_mcp.server import list_catalogs

    mock_client.list_catalogs.side_effect = QueryTimeoutError(
        "Query cancelled after exceeding the 5-minute timeout."
    )

    result = asyncio.run(list_catalogs())

    assert "timeout" in result.lower()


# ---------------------------------------------------------------------------
# MCP instructions contain concurrency/timeout info
# ---------------------------------------------------------------------------


def test_mcp_instructions_contain_constraints():
    """Test that MCP server instructions document concurrency and timeout limits."""
    from trino_mcp.server import mcp

    instructions = mcp.instructions
    assert "Concurrency limit" in instructions
    assert "timeout" in instructions.lower()
    assert "one at a time" in instructions.lower() or "wait" in instructions.lower()
