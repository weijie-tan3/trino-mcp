# Trino MCP Server

A simple Model Context Protocol (MCP) server for Trino query engine with OAuth support (without explicit JWT tokens).

## Quick Start (TLDR)

**Using with VS Code?** Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "trino": {
      "command": "uvx",
      "args": ["trino-mcp"],
      "env": {
        "TRINO_HOST": "${trino_host_address}",
        "TRINO_USER": "${env:USER}",
        "AUTH_METHOD": "OAuth2"
      }
    }
  }
}
```

**Want to run standalone?**
```bash
# Set your Trino connection
export TRINO_HOST=localhost
export TRINO_PORT=8080
export TRINO_USER=trino

# Run directly (no installation needed)
uvx trino-mcp
```

That's it! The server will connect to your Trino cluster and provide query capabilities.

---

## Features

- **Core Trino Operations**: Query catalogs, schemas, tables, and execute SQL
- **OAuth Support**: Built-in OAuth2 authentication without requiring explicit JWT tokens
- **Basic Authentication**: Also supports username/password authentication
- **Simple & Focused**: Core Trino features without over-complication
- **uvx Compatible**: Run directly with `uvx` without installation

## Prerequisites

- Python 3.10 or higher
- A running Trino server
- (Optional) Trino credentials for authentication

## Setup & Configuration

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "trino": {
      "command": "uvx",
      "args": ["trino-mcp"],
      "env": {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino"
      }
    }
  }
}
```

**For local development:**
```json
{
  "mcpServers": {
    "trino": {
      "command": "uvx",
      "args": ["--from", "/path/to/trino-mcp", "trino-mcp"],
      "env": {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino"
      }
    }
  }
}
```

### Using with VS Code

Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "trino": {
      "command": "uvx",
      "args": ["trino-mcp"],
      "env": {
        "TRINO_HOST": "${trino_host_address}",
        "TRINO_USER": "${env:USER}",
        "AUTH_METHOD": "OAuth2"
      }
    }
  }
}
```

**For local development:**
```json
{
  "servers": {
    "trino": {
      "command": "uvx",
      "args": ["--from", ".", "trino-mcp"],
      "env": {
        "TRINO_HOST": "${input:trino_host}",
        "TRINO_PORT": "${input:trino_port}",
        "TRINO_USER": "${input:trino_user}"
      }
    }
  }
}
```

### Standalone Usage

You can also run the server standalone without an MCP client:

```bash
# Run directly with uvx (no installation needed)
uvx trino-mcp

# Or run from local repository
uvx --from . trino-mcp
```

### Environment Variables

Configure the server using environment variables or a `.env` file:

```bash
# Required
TRINO_HOST=localhost              # Your Trino server hostname
TRINO_PORT=8080                   # Trino server port
TRINO_USER=trino                  # Username for authentication
TRINO_HTTP_SCHEME=http            # http or https

# Optional
TRINO_CATALOG=my_catalog          # Default catalog
TRINO_SCHEMA=my_schema            # Default schema

# Authentication (choose one):
TRINO_PASSWORD=your_password      # For basic authentication
TRINO_OAUTH_TOKEN=your_token      # For OAuth2 authentication
```

## Installation Options

If you prefer to install the package instead of using `uvx`:

### Option 1: Install with uv

```bash
# From PyPI (once published)
uv pip install trino-mcp

# From local directory
uv pip install .

# Run the server
trino-mcp
```

### Option 2: Development Installation

```bash
# Install in editable mode
uv pip install -e .

# Run the server
python -m trino_mcp.server
```

## Available Tools

### `list_catalogs`
List all available catalogs in the Trino cluster.

**Parameters**: None

**Example**:
```
list_catalogs()
```

### `list_schemas`
List all schemas in a specific catalog.

**Parameters**:
- `catalog` (string, required): The catalog name

**Example**:
```
list_schemas(catalog="hive")
```

### `list_tables`
List all tables in a specific schema.

**Parameters**:
- `catalog` (string, required): The catalog name
- `schema` (string, required): The schema name

**Example**:
```
list_tables(catalog="hive", schema="default")
```

### `describe_table`
Describe the structure of a table (columns, types, comments).

**Parameters**:
- `table` (string, required): The table name
- `catalog` (string, optional): The catalog name
- `schema` (string, optional): The schema name

**Example**:
```
describe_table(table="my_table", catalog="hive", schema="default")
```

### `execute_query`
Execute a SQL query and return the results in JSON format.

**Parameters**:
- `query` (string, required): The SQL query to execute

**Example**:
```
execute_query(query="SELECT * FROM hive.default.my_table LIMIT 10")
```

### `show_create_table`
Show the CREATE TABLE statement for a table.

**Parameters**:
- `table` (string, required): The table name
- `catalog` (string, optional): The catalog name
- `schema` (string, optional): The schema name

**Example**:
```
show_create_table(table="my_table", catalog="hive", schema="default")
```

### `get_table_stats`
Get statistics for a table.

**Parameters**:
- `table` (string, required): The table name
- `catalog` (string, optional): The catalog name
- `schema` (string, optional): The schema name

**Example**:
```
get_table_stats(table="my_table", catalog="hive", schema="default")
```

## OAuth Authentication

This server is designed to work with Trino's OAuth2 authentication mechanism. The Trino Python client supports OAuth2 authentication through a redirect handler mechanism that doesn't require you to manually manage JWT tokens.

### How OAuth Works with Trino

1. **Server Configuration**: Configure your Trino cluster with OAuth2 authentication
2. **Client Connection**: The Trino Python client handles the OAuth2 flow automatically
3. **Token Management**: Tokens are managed by the client library - no manual JWT handling required

For basic username/password authentication, simply set `TRINO_PASSWORD` in your environment.

**Note**: OAuth2 support in the Trino Python client requires implementing a redirect handler. This server provides the foundation for OAuth2 integration. For production use with OAuth2, you may need to extend the configuration to implement your specific OAuth2 flow based on your identity provider.

## Architecture

```
trino-mcp/
├── src/
│   └── trino_mcp/
│       ├── __init__.py
│       ├── config.py      # Configuration management
│       ├── client.py      # Trino client wrapper
│       └── server.py      # MCP server implementation
├── pyproject.toml         # Project configuration
├── .env.example          # Example environment variables
└── README.md             # This file
```

## Development

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests (when available)
pytest

# Format code
black src/

# Type checking
mypy src/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


For issues and questions:
- Open an issue on GitHub
- Check Trino documentation: https://trino.io/docs/
- Check MCP documentation: https://modelcontextprotocol.io/
