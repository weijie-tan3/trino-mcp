# Trino MCP Server

[![CI](https://github.com/weijie-tan3/trino-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/weijie-tan3/trino-mcp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/weijie-tan3/trino-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/weijie-tan3/trino-mcp)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/trino-mcp.svg)](https://pypi.org/project/trino-mcp/)

A simple Model Context Protocol (MCP) server for Trino query engine with OAuth and Azure Service Principal (SPN) support.

## Quick Start (TL;DR)

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

- **Core Trino Operations** without over-complication: Query catalogs, schemas, tables, and execute SQL
- **Multiple Auth Methods**: OAuth2, Azure Service Principal (SPN, >=v0.1.4), basic username/password, or no auth
  - **Azure SPN with Auto-Refresh**: Tokens are automatically refreshed before each request — no expiry issues for long-running servers
- **uvx Compatible**: Run directly with `uvx` without installation
- **Double-Write Protection**: Two layers of safety — separate read-only and read-write tools (`execute_query_read_only` vs `execute_query`), plus an `ALLOW_WRITE_QUERIES` configuration flag that must be explicitly enabled before any write query can run
- **File Export** (>=v0.2.0): Write query results directly to disk (JSON or CSV, derived from file extension) to enable subsequent processing by other tools while preventing LLM hallucination on raw data
- **Query Watermarking**: Automatically adds watermark comments to queries for tracking and auditing (includes username and version).
  - Support for custom watermark key-value pairs via `TRINO_MCP_CUSTOM_WATERMARK` (>=v0.2.0)

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
TRINO_PORT=8080                   # Trino server port (auto-set to 443 for Azure SPN/OAuth2)
TRINO_USER=trino                  # Username (auto-detected from JWT for Azure SPN)
TRINO_HTTP_SCHEME=http            # http or https (auto-set to https for Azure SPN/OAuth2)

# Optional
TRINO_CATALOG=my_catalog          # Default catalog
TRINO_SCHEMA=my_schema            # Default schema

# Authentication method: PASSWORD (default), OAUTH2, AZURE_SPN, or NONE
AUTH_METHOD=PASSWORD

# Option 1: Basic Authentication (AUTH_METHOD=PASSWORD)
TRINO_PASSWORD=your_password

# Option 2: OAuth2 (AUTH_METHOD=OAUTH2)
# Uses Trino's built-in OAuth2 flow (browser-based)

# Option 3: Azure Service Principal (AUTH_METHOD=AZURE_SPN)
# See "Azure SPN Authentication" section below

# Option 4: No auth (AUTH_METHOD=NONE)

# Security
ALLOW_WRITE_QUERIES=true          # Enable write operations (INSERT, UPDATE, DELETE, etc.)
                                  # Disabled by default for safety
                                  # accepts `true`, `1`, or `yes`

# Custom Watermark
# JSON object mapping watermark keys to environment variable names.
# Values of those env vars are included in query watermark comments.
TRINO_MCP_CUSTOM_WATERMARK='{"wtm_key": "ENV_VARIABLE_NAME_TO_CATCH"}'
```

## Available Tools

The Trino MCP server provides the following tools (see [`server.py`](src/trino_mcp/server.py) for full details):
- `list_catalogs` - List all available Trino catalogs
- `list_schemas` - List all schemas in a catalog
- `list_tables` - List all tables in a schema
- `describe_table` - Describe the structure of a table
- `execute_query_read_only` - Execute read-only SQL queries (SELECT, SHOW, DESCRIBE, EXPLAIN)
- `execute_query` - Execute any SQL query (requires `ALLOW_WRITE_QUERIES=true` for write operations)
- `show_create_table` - Show the CREATE TABLE statement for a table
- `get_table_stats` - Get statistics for a table

### Exporting Query Results to File

Both `execute_query` and `execute_query_read_only` support an `output_file` parameter that writes results directly to disk instead of returning them to the AI. This is useful for:

- **Preventing LLM hallucination**: Large result sets passed through the AI may be summarized, truncated, or hallucinated. Writing to a file ensures data integrity.
- **Subsequent processing**: The exported file can be read by other tools (e.g., a Python script) for accurate data processing without AI interpretation.

The output format is automatically derived from the file extension:
- `.csv` → CSV format (with header row)
- `.json` (or any other extension) → JSON format

When `output_file` is set, only a confirmation message with the row count is returned to the AI — the raw data never passes through the model.

## Authentication

### OAuth2

Set `AUTH_METHOD=OAUTH2`. The Trino Python client handles the OAuth2 flow automatically through a browser-based redirect — no manual JWT handling required.

### Azure Service Principal (SPN)

For non-interactive / CI environments using Azure AD. Install with Azure extras:

```bash
# pip
pip install trino-mcp[azure]

# uv
uv pip install trino-mcp[azure]

# uvx (install azure-identity alongside)
uvx --from "trino-mcp>=0.1.4" --with azure-identity trino-mcp
```

The server tries three credential methods in order:

1. **`az login` (AzureCliCredential)** — Easiest for local dev. Just run `az login --service-principal` beforehand.
2. **Environment variables (ClientSecretCredential)** — Best for CI/CD. Set `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, and `AZURE_TENANT_ID`.
3. **DefaultAzureCredential** — Fallback for managed identity, etc.

`AZURE_SCOPE` is always required (the Trino server's Azure AD app scope, e.g. `api://<trino-app-id>/.default`).

#### Option A: Using `az login` (local development)

```bash
# Login as the service principal
az login --service-principal \
    --username "$AZURE_CLIENT_ID" \
    --password "$AZURE_CLIENT_SECRET" \
    --tenant "$AZURE_TENANT_ID" \
    --allow-no-subscriptions
```

`.env`:
```bash
AUTH_METHOD=AZURE_SPN
AZURE_SCOPE=api://your-trino-app-id/.default
TRINO_HOST=trino.example.com
TRINO_CATALOG=hive
TRINO_SCHEMA=default
```

#### Option B: Using environment variables (CI/CD)

`.env`:
```bash
AUTH_METHOD=AZURE_SPN
AZURE_SCOPE=api://your-trino-app-id/.default
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
TRINO_HOST=trino.example.com
TRINO_CATALOG=hive
TRINO_SCHEMA=default
```

#### VS Code MCP config for Azure SPN

```json
{
  "servers": {
    "trino": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "trino-mcp>=0.1.4", "--with", "azure-identity", "trino-mcp"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

The server reads from `.env` automatically — no need to duplicate env vars in `mcp.json`.

> **Token auto-refresh**: The server automatically refreshes Azure tokens before each Trino request, so it works reliably for long-running sessions without expiry issues.

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

See [docs/dev.md](docs/dev.md) for release instructions.

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

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


For issues and questions:
- [Open an issue on GitHub](https://github.com/weijie-tan3/trino-mcp/issues)
- Check Trino documentation: https://trino.io/docs/
- Check MCP documentation: https://modelcontextprotocol.io/
