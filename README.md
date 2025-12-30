# Trino MCP Server

[![CI](https://github.com/weijie-tan3/trino-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/weijie-tan3/trino-mcp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/weijie-tan3/trino-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/weijie-tan3/trino-mcp)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/trino-mcp.svg)](https://pypi.org/project/trino-mcp/)

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
        // "ALLOW_WRITE_QUERIES": "true"  // Enable write operations (disabled by default)
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
- **Write Protection**: Separate tools (`execute_query` and `execute_query_read_only`) with `ALLOW_WRITE_QUERIES` configuration to prevent accidental database modifications
- **Query Watermarking**: Automatically adds watermark comments to queries for tracking and auditing (includes username and version)

## Prerequisites

- Python 3.10 or higher
- A running Trino server
- (Optional) Trino credentials for authentication
- (Optional) [uvx](https://docs.astral.sh/uv/guides/tools/)

## Setup & Configuration

General recommendation: using `uvx` or `uv`.
```bash
# From PyPI
uv pip install trino-mcp

# From PyPI
uvx trino-mcp

# Clone to local directory and install
uv pip install .
trino-mcp
```

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
        // "ALLOW_WRITE_QUERIES": "true"  // Enable write operations if needed
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
        // "ALLOW_WRITE_QUERIES": "true"  // Enable write operations if needed
      }
    }
  }
}
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

# Security
ALLOW_WRITE_QUERIES=true          # Enable write operations (INSERT, UPDATE, DELETE, etc.)
                                  # Disabled by default for safety
```

## Available Tools

The Trino MCP server provides the following tools. For the most up-to-date documentation, see the [CI-generated tool documentation](../../actions) (available as artifacts in CI runs).

**Quick summary:**
- `list_catalogs` - List all available Trino catalogs
- `list_schemas` - List all schemas in a catalog
- `list_tables` - List all tables in a schema
- `describe_table` - Describe the structure of a table
- `execute_query_read_only` - Execute read-only SQL queries (SELECT, SHOW, DESCRIBE, EXPLAIN)
- `execute_query` - Execute any SQL query (requires `ALLOW_WRITE_QUERIES=true` for write operations)
- `show_create_table` - Show the CREATE TABLE statement for a table
- `get_table_stats` - Get statistics for a table

To generate the detailed tool documentation locally:
```bash
python3 scripts/generate_tool_docs.py
# This creates TOOLS.md and tools.json with complete documentation
```

## OAuth Authentication

This server is designed to work with Trino's OAuth2 authentication mechanism. The Trino Python client supports OAuth2 authentication through a redirect handler mechanism that doesn't require you to manually manage JWT tokens.

### How OAuth Works with Trino

1. **Server Configuration**: Configure your Trino cluster with OAuth2 authentication
2. **Client Connection**: The Trino Python client handles the OAuth2 flow automatically
3. **Token Management**: Tokens are managed by the client library - no manual JWT handling required

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

### Publishing a New Version
You can do it all in GitHub interface
1. Update the version in `pyproject.toml`
2. Create a GitHub release + new tag.
3. CI will automatically build and publish to PyPI

### Known Issues

**Pytest exits with code 137 (SIGKILL)**

If tests hang or exit with code 137, there may be stuck `trino-mcp` or `uv` processes consuming resources. Try killing them:

```bash
# Check for stuck processes
ps aux | grep -E "trino-mcp|uvx" | grep -v grep

# Kill if found
pkill -f trino-mcp
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


For issues and questions:
- Open an issue on GitHub
- Check Trino documentation: https://trino.io/docs/
- Check MCP documentation: https://modelcontextprotocol.io/
