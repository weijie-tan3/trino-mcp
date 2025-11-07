# Trino MCP Server - Project Summary

## Overview

A simple, focused Model Context Protocol (MCP) server for Trino query engine with OAuth support capability.

## Project Structure

```
trino-mcp/
├── src/
│   └── trino_mcp/
│       ├── __init__.py      # Package initialization
│       ├── config.py         # Configuration management (OAuth support)
│       ├── client.py         # Trino client wrapper
│       └── server.py         # MCP server implementation with 7 core tools
├── examples/
│   └── basic_usage.py        # Example Python usage
├── .vscode/
│   └── mcp.json             # VS Code MCP configuration
├── pyproject.toml           # Project metadata and dependencies
├── .env.example             # Environment variable template
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
├── README.md               # Full documentation
├── QUICKSTART.md           # Quick start guide
└── validate.py             # Installation validation script
```

## Core Features

### 7 Essential Trino Tools

1. **list_catalogs** - List all available Trino catalogs
2. **list_schemas** - List schemas in a catalog
3. **list_tables** - List tables in a schema
4. **describe_table** - Get table structure (columns, types)
5. **execute_query** - Execute arbitrary SQL queries
6. **show_create_table** - Show CREATE TABLE DDL
7. **get_table_stats** - Get table statistics

### Authentication

- **Basic Authentication**: Username/password
- **OAuth2 Ready**: Infrastructure for OAuth2 (requires redirect handler implementation)

### Configuration

Environment-based configuration via `.env` file:
- TRINO_HOST, TRINO_PORT, TRINO_USER
- Optional: TRINO_CATALOG, TRINO_SCHEMA
- Authentication: TRINO_PASSWORD

## Technologies Used

- **Python 3.11+**
- **MCP SDK** (>=1.6.0) - Model Context Protocol
- **Trino Python Client** (>=0.333.0) - Trino connectivity
- **python-dotenv** - Environment configuration

## Installation Methods

1. **uvx (Recommended)**: `uvx --from . trino-mcp`
2. **uv install**: `uv pip install . && trino-mcp`
3. **Development**: `uv pip install -e . && python -m trino_mcp.server`

## Integration

### Claude Desktop

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

### VS Code

Configuration provided in `.vscode/mcp.json` with input prompts.

## Design Principles

1. **Simplicity**: Core Trino features only, no over-complication
2. **uvx Compatible**: Can run directly without installation
3. **OAuth Ready**: Infrastructure for OAuth2 without explicit JWT token management
4. **Type Safe**: Full type hints throughout
5. **Error Handling**: Graceful error handling with helpful messages

## Key Implementation Details

### Configuration (config.py)
- Environment-based configuration loading
- Support for basic authentication
- OAuth2 infrastructure (extensible)
- Optional default catalog/schema

### Client (client.py)
- Wraps Trino Python DBAPI
- JSON result serialization
- Fallback to configured defaults for catalog/schema
- Clean error propagation

### Server (server.py)
- FastMCP-based implementation
- 7 core tools exposed via MCP
- Type-safe tool parameters
- Stdio-based MCP communication

## Testing & Validation

- **validate.py**: Comprehensive validation script
  - Environment check
  - Dependency verification
  - Connection testing
  - MCP server validation

- **examples/basic_usage.py**: Example Python client usage

## Documentation

- **README.md**: Comprehensive documentation
- **QUICKSTART.md**: Quick start guide (5 minutes)
- **Inline**: Extensive docstrings and type hints

## Development Status

- ✅ Core Trino query operations
- ✅ Basic authentication
- ✅ uvx compatibility
- ✅ MCP integration
- ✅ Type safety
- ✅ Documentation
- ⚠️ OAuth2 (infrastructure present, needs redirect handler)
- 🔜 Advanced Iceberg operations (optional future enhancement)

## License

MIT License - Free and open source

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Trino Documentation](https://trino.io/docs/)
- [Trino Python Client](https://github.com/trinodb/trino-python-client)
- Based on:
  - [mcp-python-starter](https://github.com/SamMorrowDrums/mcp-python-starter)
  - [mcp-trino-python](https://github.com/alaturqua/mcp-trino-python)
  - [canonical-mcp](https://github.com/github/canonical-mcp)
