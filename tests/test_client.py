"""Tests for Trino client module."""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from trino_mcp import __version__
from trino_mcp.client import TrinoClient
from trino_mcp.config import TrinoConfig


def _expected_watermark(user: str = "trino", **custom) -> str:
    """Build expected JSON watermark comment."""
    data = {"trino_mcp_version": __version__, "user": user}
    if custom:
        data.update(sorted(custom.items()))
    return f"-- {json.dumps(data)} --"


@pytest.fixture
def config():
    """Create a test configuration."""
    return TrinoConfig(
        host="localhost",
        port=8080,
        user="trino",
        catalog="test_catalog",
        schema="test_schema",
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


def test_execute_query_raw_with_results(config, mock_connection):
    """Test execute_query_raw returns native Python data structures with results."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("col1",), ("col2",)]
    mock_cursor.fetchall.return_value = [("val1", "val2"), ("val3", "val4")]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.execute_query_raw("SELECT * FROM test")

    # Should return a list of dictionaries, not a JSON string
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {"col1": "val1", "col2": "val2"}
    assert result[1] == {"col1": "val3", "col2": "val4"}


def test_execute_query_raw_without_results(config, mock_connection):
    """Test execute_query_raw returns native Python data structures without results."""
    mock_cursor = MagicMock()
    mock_cursor.description = None
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.execute_query_raw("CREATE TABLE test (id INT)")

    # Should return a dictionary, not a JSON string
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "executed successfully" in result["message"]


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
    mock_cursor.execute.assert_called_with(
        f"{_expected_watermark()}\nSHOW SCHEMAS FROM test_catalog"
    )


def test_list_schemas_with_default(config, mock_connection):
    """Test listing schemas using default catalog."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Schema",)]
    mock_cursor.fetchall.return_value = [("schema1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    schemas = client.list_schemas("")

    assert schemas == ["schema1"]
    mock_cursor.execute.assert_called_with(
        f"{_expected_watermark()}\nSHOW SCHEMAS FROM test_catalog"
    )


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
    mock_cursor.execute.assert_called_with(
        f"{_expected_watermark()}\nSHOW TABLES FROM catalog1.schema1"
    )


def test_list_tables_with_defaults(config, mock_connection):
    """Test listing tables using default catalog and schema."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Table",)]
    mock_cursor.fetchall.return_value = [("table1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    tables = client.list_tables("", "")

    assert tables == ["table1"]
    mock_cursor.execute.assert_called_with(
        f"{_expected_watermark()}\nSHOW TABLES FROM test_catalog.test_schema"
    )


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
    mock_cursor.execute.assert_called_with(
        f"{_expected_watermark()}\nDESCRIBE catalog1.schema1.table1"
    )


def test_show_create_table(config, mock_connection):
    """Test showing CREATE TABLE statement."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("Create Table",)]
    mock_cursor.fetchall.return_value = [("CREATE TABLE test (id INT)",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    result = client.show_create_table("catalog1", "schema1", "table1")

    assert result == "CREATE TABLE test (id INT)"
    mock_cursor.execute.assert_called_with(
        f"{_expected_watermark()}\nSHOW CREATE TABLE catalog1.schema1.table1"
    )


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
    mock_cursor.execute.assert_called_with(
        f"{_expected_watermark()}\nSHOW STATS FOR catalog1.schema1.table1"
    )


def test_watermark_addition(config, mock_connection):
    """Test that watermark is correctly added to queries."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("result",)]
    mock_cursor.fetchall.return_value = [("1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)

    # Test with a simple query
    result = client.execute_query("SELECT 1")

    # Verify the watermark was added
    expected_query = f"{_expected_watermark()}\nSELECT 1"
    mock_cursor.execute.assert_called_with(expected_query)

    # Verify the watermark is a JSON comment
    call_args = mock_cursor.execute.call_args[0][0]
    assert call_args.startswith(f"{_expected_watermark()}\n")


def test_watermark_with_different_username(mock_connection):
    """Test that watermark uses the configured username."""
    config = TrinoConfig(
        host="localhost",
        port=8080,
        user="custom_user",
        catalog="test_catalog",
        schema="test_schema",
    )

    mock_cursor = MagicMock()
    mock_cursor.description = [("result",)]
    mock_cursor.fetchall.return_value = [("1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)

    # Test with a simple query
    result = client.execute_query("SELECT 1")

    # Verify the watermark includes the correct username
    expected_query = f"{_expected_watermark(user='custom_user')}\nSELECT 1"
    mock_cursor.execute.assert_called_with(expected_query)


def test_watermark_with_custom_watermark(mock_connection):
    """Test that custom watermark key-value pairs are included."""
    config = TrinoConfig(
        host="localhost",
        port=8080,
        user="trino",
        catalog="test_catalog",
        schema="test_schema",
        custom_watermark={"wtm_key": "my-app"},
    )

    mock_cursor = MagicMock()
    mock_cursor.description = [("result",)]
    mock_cursor.fetchall.return_value = [("1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    client.execute_query("SELECT 1")

    expected_query = f"{_expected_watermark(wtm_key='my-app')}\nSELECT 1"
    mock_cursor.execute.assert_called_with(expected_query)


def test_watermark_with_multiple_custom_keys(mock_connection):
    """Test that multiple custom watermark keys are included."""
    config = TrinoConfig(
        host="localhost",
        port=8080,
        user="trino",
        catalog="test_catalog",
        schema="test_schema",
        custom_watermark={"team": "data-eng", "env": "prod"},
    )

    mock_cursor = MagicMock()
    mock_cursor.description = [("result",)]
    mock_cursor.fetchall.return_value = [("1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    client.execute_query("SELECT 1")

    expected_query = f"{_expected_watermark(env='prod', team='data-eng')}\nSELECT 1"
    mock_cursor.execute.assert_called_with(expected_query)


def test_watermark_without_custom_watermark(mock_connection):
    """Test that watermark works normally when custom_watermark is None."""
    config = TrinoConfig(
        host="localhost",
        port=8080,
        user="trino",
        catalog="test_catalog",
        schema="test_schema",
        custom_watermark=None,
    )

    mock_cursor = MagicMock()
    mock_cursor.description = [("result",)]
    mock_cursor.fetchall.return_value = [("1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    client.execute_query("SELECT 1")

    expected_query = f"{_expected_watermark()}\nSELECT 1"
    mock_cursor.execute.assert_called_with(expected_query)


def test_watermark_custom_values_with_newlines_do_not_escape_comment(mock_connection):
    """Test that newlines stripped at config load time cannot escape the SQL comment."""
    env = {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "TRINO_MCP_CUSTOM_WATERMARK": '{"key": "INJECTED_VAR"}',
        "INJECTED_VAR": "safe-value\ninjected-sql",
    }
    with patch.dict("os.environ", env):
        from trino_mcp.config import load_config
        config = load_config()

    mock_cursor = MagicMock()
    mock_cursor.description = [("result",)]
    mock_cursor.fetchall.return_value = [("1",)]
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)
    client.execute_query("SELECT 1")

    call_args = mock_cursor.execute.call_args[0][0]
    # The newline in the env var value is stripped, so it stays inside the comment.
    # Verify no extra lines are injected before the actual query.
    lines = call_args.split("\n")
    assert lines[0].startswith("-- ")
    assert lines[0].endswith(" --")
    # The sanitized text is confined to the comment line (no literal newline escape)
    assert lines[1] == "SELECT 1"
    assert len(lines) == 2


def test_list_catalogs_with_unexpected_response(config, mock_connection):
    """Test that list_catalogs raises error for unexpected response."""
    mock_cursor = MagicMock()
    mock_cursor.description = None  # No results
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)

    with pytest.raises(RuntimeError, match="Expected list of results from SHOW CATALOGS"):
        client.list_catalogs()


def test_list_schemas_with_unexpected_response(config, mock_connection):
    """Test that list_schemas raises error for unexpected response."""
    mock_cursor = MagicMock()
    mock_cursor.description = None  # No results
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)

    with pytest.raises(RuntimeError, match="Expected list of results from SHOW SCHEMAS"):
        client.list_schemas("test_catalog")


def test_list_tables_with_unexpected_response(config, mock_connection):
    """Test that list_tables raises error for unexpected response."""
    mock_cursor = MagicMock()
    mock_cursor.description = None  # No results
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)

    with pytest.raises(RuntimeError, match="Expected list of results from SHOW TABLES"):
        client.list_tables("catalog1", "schema1")


def test_show_create_table_with_unexpected_response(config, mock_connection):
    """Test that show_create_table raises error for unexpected response."""
    mock_cursor = MagicMock()
    mock_cursor.description = None  # No results
    mock_connection.cursor.return_value = mock_cursor

    client = TrinoClient(config)

    with pytest.raises(RuntimeError, match="Expected list of results from SHOW CREATE TABLE"):
        client.show_create_table("catalog1", "schema1", "table1")
