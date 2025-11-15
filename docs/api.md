# API Reference

Complete API reference for the Trino MCP Server.

## Module Structure

```
trino_mcp/
├── __init__.py      # Package initialization and version
├── config.py        # Configuration management
├── client.py        # Trino client wrapper
└── server.py        # MCP server implementation
```

## Configuration Module

### TrinoConfig

Configuration class for Trino connection settings.

**Attributes:**

- `host` (str): Trino server hostname
- `port` (int): Trino server port
- `user` (str): Username for authentication
- `password` (str | None): Password for basic authentication
- `oauth_token` (str | None): OAuth token for OAuth2 authentication
- `http_scheme` (str): HTTP scheme (http/https)
- `catalog` (str | None): Default catalog
- `schema` (str | None): Default schema
- `verify_ssl` (bool): Whether to verify SSL certificates
- `ssl_cert` (str | None): Path to SSL certificate

### load_config()

Load configuration from environment variables.

**Returns:** `TrinoConfig` - Configuration object

**Environment Variables:**

See [Configuration](configuration.md) for complete list.

**Example:**

```python
from trino_mcp.config import load_config

config = load_config()
print(f"Connecting to {config.host}:{config.port}")
```

---

## Client Module

### TrinoClient

Wrapper around the Trino Python client for executing queries and metadata operations.

**Methods:**

#### `__init__(config: TrinoConfig)`

Initialize the Trino client with configuration.

**Parameters:**
- `config` (TrinoConfig): Trino configuration object

**Example:**

```python
from trino_mcp.config import load_config
from trino_mcp.client import TrinoClient

config = load_config()
client = TrinoClient(config)
```

#### `list_catalogs() -> list[str]`

List all available catalogs.

**Returns:** List of catalog names

**Raises:** `Exception` if query fails

**Example:**

```python
catalogs = client.list_catalogs()
print(catalogs)  # ['system', 'hive', 'mysql']
```

#### `list_schemas(catalog: str) -> list[str]`

List all schemas in a catalog.

**Parameters:**
- `catalog` (str): Catalog name

**Returns:** List of schema names

**Raises:** `Exception` if query fails

**Example:**

```python
schemas = client.list_schemas("hive")
print(schemas)  # ['default', 'production', 'staging']
```

#### `list_tables(catalog: str, schema: str) -> list[str]`

List all tables in a schema.

**Parameters:**
- `catalog` (str): Catalog name
- `schema` (str): Schema name

**Returns:** List of table names

**Raises:** `Exception` if query fails

**Example:**

```python
tables = client.list_tables("hive", "production")
print(tables)  # ['customers', 'orders', 'products']
```

#### `describe_table(table: str, catalog: str | None = None, schema: str | None = None) -> list[dict]`

Describe table structure.

**Parameters:**
- `table` (str): Table name
- `catalog` (str | None): Catalog name (uses default if None)
- `schema` (str | None): Schema name (uses default if None)

**Returns:** List of column dictionaries with keys: name, type, comment

**Raises:** `Exception` if query fails

**Example:**

```python
columns = client.describe_table("customers", "hive", "production")
for col in columns:
    print(f"{col['name']} ({col['type']})")
```

#### `execute_query(query: str) -> list[dict]`

Execute a SQL query and return results.

**Parameters:**
- `query` (str): SQL query to execute

**Returns:** List of row dictionaries

**Raises:** `Exception` if query fails

**Example:**

```python
results = client.execute_query("SELECT * FROM hive.production.customers LIMIT 5")
for row in results:
    print(row)
```

#### `show_create_table(table: str, catalog: str | None = None, schema: str | None = None) -> str`

Get CREATE TABLE statement.

**Parameters:**
- `table` (str): Table name
- `catalog` (str | None): Catalog name (uses default if None)
- `schema` (str | None): Schema name (uses default if None)

**Returns:** CREATE TABLE SQL statement

**Raises:** `Exception` if query fails

**Example:**

```python
create_stmt = client.show_create_table("customers", "hive", "production")
print(create_stmt)
```

#### `get_table_stats(table: str, catalog: str | None = None, schema: str | None = None) -> dict`

Get table statistics.

**Parameters:**
- `table` (str): Table name
- `catalog` (str | None): Catalog name (uses default if None)
- `schema` (str | None): Schema name (uses default if None)

**Returns:** Dictionary with statistics

**Raises:** `Exception` if query fails

**Example:**

```python
stats = client.get_table_stats("customers", "hive", "production")
print(f"Row count: {stats.get('row_count', 'N/A')}")
```

---

## Server Module

### MCP Tools

The server module exposes several tools through the Model Context Protocol:

#### `list_catalogs() -> str`

MCP tool for listing catalogs.

**Returns:** Newline-separated list of catalog names

#### `list_schemas(catalog: str) -> str`

MCP tool for listing schemas.

**Parameters:**
- `catalog` (str): Catalog name

**Returns:** Newline-separated list of schema names

#### `list_tables(catalog: str, schema: str) -> str`

MCP tool for listing tables.

**Parameters:**
- `catalog` (str): Catalog name
- `schema` (str): Schema name

**Returns:** Newline-separated list of table names

#### `describe_table(table: str, catalog: str | None = None, schema: str | None = None) -> str`

MCP tool for describing table structure.

**Parameters:**
- `table` (str): Table name
- `catalog` (str | None): Catalog name
- `schema` (str | None): Schema name

**Returns:** Formatted table description

#### `execute_query(query: str) -> str`

MCP tool for executing SQL queries.

**Parameters:**
- `query` (str): SQL query

**Returns:** JSON-formatted query results

#### `show_create_table(table: str, catalog: str | None = None, schema: str | None = None) -> str`

MCP tool for showing CREATE TABLE statement.

**Parameters:**
- `table` (str): Table name
- `catalog` (str | None): Catalog name
- `schema` (str | None): Schema name

**Returns:** CREATE TABLE SQL statement

#### `get_table_stats(table: str, catalog: str | None = None, schema: str | None = None) -> str`

MCP tool for getting table statistics.

**Parameters:**
- `table` (str): Table name
- `catalog` (str | None): Catalog name
- `schema` (str | None): Schema name

**Returns:** Formatted table statistics

### `main()`

Entry point for the MCP server.

Starts the FastMCP server and handles stdio communication.

**Example:**

```bash
# Run from command line
trino-mcp

# Or from Python
python -m trino_mcp.server
```

---

## Data Types

### Column Information

Dictionary with column information:

```python
{
    "name": str,       # Column name
    "type": str,       # Data type (e.g., "bigint", "varchar")
    "comment": str     # Column comment/description
}
```

### Query Result Row

Dictionary with query result row:

```python
{
    "column_name": value,  # Column name mapped to value
    ...
}
```

### Table Statistics

Dictionary with table statistics:

```python
{
    "row_count": int,      # Number of rows
    "data_size": str,      # Data size (e.g., "2.5 GB")
    "num_partitions": int, # Number of partitions
    "last_modified": str   # Last modification timestamp
}
```

---

## Error Handling

All methods may raise exceptions. Error messages are formatted as:

```
Error [operation]: [error message]
```

Examples:
- `Error listing catalogs: Connection refused`
- `Error executing query: Permission denied`
- `Error describing table: Table does not exist`

---

## Logging

The server uses Python's `logging` module. Configure logging level:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

Log levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about operations
- `WARNING`: Warning messages
- `ERROR`: Error messages

---

## Version Information

```python
import trino_mcp

print(trino_mcp.__version__)  # e.g., "0.1.0"
```

---

## Next Steps

- [Examples](examples.md) - See usage examples
- [Available Tools](tools.md) - Tool reference
- [Configuration](configuration.md) - Configuration options
