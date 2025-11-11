# Trino MCP Server

A simple Model Context Protocol (MCP) server for Trino query engine with OAuth support (without explicit JWT tokens).

## Features

- **Core Trino Operations**: Query catalogs, schemas, tables, and execute SQL
- **OAuth Support**: Built-in OAuth2 authentication without requiring explicit JWT tokens
- **Basic Authentication**: Also supports username/password authentication
- **Simple & Focused**: Core Trino features without over-complication
- **uvx Compatible**: Run directly with `uvx` without installation

## Prerequisites

- Python 3.11 or higher
- A running Trino server
- (Optional) Trino credentials for authentication

## Installation

### Option 1: Run with uvx (Recommended)

Once published to PyPI, you can run directly:

```bash
uvx trino-mcp
```

For development or local usage:

```bash
# Run directly from the repository
uvx --from . trino-mcp
```

### Option 2: Install with uv

```bash
# From PyPI (once published)
uv pip install trino-mcp

# From local directory
uv pip install .

# Run the server
trino-mcp
```

### Option 3: Development Installation

```bash
# Install in editable mode
uv pip install -e .

# Run the server
python -m trino_mcp.server
```

## Configuration

Create a `.env` file in your working directory or set environment variables:

```bash
# Basic Configuration
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=trino
TRINO_HTTP_SCHEME=http

# Optional: Default catalog and schema
TRINO_CATALOG=my_catalog
TRINO_SCHEMA=my_schema

# Authentication Options (choose one):

# Option 1: Basic Authentication
TRINO_PASSWORD=your_password

# Option 2: OAuth2 Authentication (without explicit JWT)
TRINO_OAUTH_TOKEN=your_oauth_token
```

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

**After publishing to PyPI:**
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

### With VS Code

Add to `.vscode/mcp.json`:

**After publishing to PyPI:**
```json
{
  "servers": {
    "trino": {
      "command": "uvx",
      "args": ["trino-mcp"],
      "env": {
        "TRINO_HOST": "${input:trino_host}",
        "TRINO_PORT": "${input:trino_port}",
        "TRINO_USER": "${input:trino_user}"
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

### OAuth Setup

To use OAuth2 authentication with your Trino cluster:

1. Configure Trino with OAuth2 (see [Trino OAuth2 docs](https://trino.io/docs/current/security/oauth2.html))
2. The authentication flow will be handled automatically by the Trino client
3. No explicit JWT token configuration needed - the client manages tokens transparently

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

### Publishing to PyPI

To publish the package to PyPI (requires PyPI credentials):

```bash
# Build the package
uv build

# Publish to PyPI (using twine or uv publish)
# First, ensure you have credentials configured
uv publish

# Or use twine
python -m pip install twine
python -m twine upload dist/*
```

Once published to PyPI, users can install the package directly:

```bash
# Using uvx (no installation required)
uvx trino-mcp

# Using uv
uv pip install trino-mcp

# Using pip
pip install trino-mcp
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Open an issue on GitHub
- Check Trino documentation: https://trino.io/docs/
- Check MCP documentation: https://modelcontextprotocol.io/
