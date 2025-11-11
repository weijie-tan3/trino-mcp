# Trino MCP Server

Model Context Protocol server for Trino query engine, with OAuth2 support.

## Quick Start

**Install:**
```bash
uvx trino-mcp
```

**Configure** (create `.env` file):
```bash
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=trino
TRINO_PASSWORD=your_password  # Optional
```

**Use with VS Code** (in `.vscode/mcp.json`):
```json
{
  "servers": {
    "trino": {
      "command": "uvx",
      "args": ["trino-mcp"],
      "env": {
        "TRINO_HOST": "trino_host_address",
        "TRINO_USER": "user_name",
        "AUTH_METHOD": "OAuth2"
      }
    }
  }
}
```

## Available Tools

- `list_catalogs()` - List all catalogs
- `list_schemas(catalog)` - List schemas in a catalog
- `list_tables(catalog, schema)` - List tables in a schema
- `describe_table(table, catalog, schema)` - Show table structure
- `execute_query(query)` - Execute SQL and return results
- `show_create_table(table, catalog, schema)` - Show CREATE TABLE statement
- `get_table_stats(table, catalog, schema)` - Get table statistics

## Development

```bash
# Clone and install
git clone https://github.com/weijie-tan3/trino-mcp.git
cd trino-mcp
uv pip install -e .

# Run tests
uv run pytest

# Run locally
uvx --from . trino-mcp
```
