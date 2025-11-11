# Trino MCP Server

Model Context Protocol server for Trino query engine, with OAuth2 support.

## Quick Start

**Install:**
```bash
uvx trino-mcp
```

**Configure** (create `.env` file):

| Variable | Required | Default | Allowed Values | Description |
|----------|----------|---------|----------------|-------------|
| `TRINO_HOST` | ✅ | `localhost` | Any hostname/IP | Trino server hostname |
| `TRINO_PORT` | ✅ | `8080` | Any port number | Trino server port |
| `TRINO_USER` | ✅ | `trino` | Any username | Trino username |
| `AUTH_METHOD` | ❌ | `PASSWORD` | `NONE`, `PASSWORD`, `OAUTH2` | Authentication method |
| `TRINO_PASSWORD` | Conditional* | - | Any password | Required if `AUTH_METHOD=PASSWORD` |
| `TRINO_HTTP_SCHEME` | ❌ | `http` | `http`, `https` | Connection protocol |
| `TRINO_CATALOG` | ❌ | - | Any catalog name | Default catalog for queries |
| `TRINO_SCHEMA` | ❌ | - | Any schema name | Default schema for queries |

**Authentication rules:**
- `AUTH_METHOD=NONE` - No authentication required
- `AUTH_METHOD=PASSWORD` - Requires `TRINO_PASSWORD` to be set
- `AUTH_METHOD=OAUTH2` - OAuth2 flow handled automatically by Trino client
- If `AUTH_METHOD` is not set, defaults to `PASSWORD`


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
