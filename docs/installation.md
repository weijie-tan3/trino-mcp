# Installation

There are several ways to install and run Trino MCP Server, depending on your needs.

## Option 1: Run with uvx (Recommended)

The easiest way to run the server without installation:

```bash
uvx trino-mcp
```

For development or local usage from the repository:

```bash
# Run directly from the repository
uvx --from . trino-mcp
```

## Option 2: Install with uv

Install the package using uv:

```bash
# From PyPI (once published)
uv pip install trino-mcp

# From local directory
uv pip install .

# Run the server
trino-mcp
```

## Option 3: Install with pip

Standard pip installation:

```bash
# From PyPI
pip install trino-mcp

# Run the server
trino-mcp
```

## Option 4: Development Installation

For development work:

```bash
# Clone the repository
git clone https://github.com/weijie-tan3/trino-mcp.git
cd trino-mcp

# Install in editable mode
uv pip install -e .

# Or with pip
pip install -e .

# Run the server
python -m trino_mcp.server
```

## Integration with MCP Clients

### Claude Desktop

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

### VS Code MCP

Add to `.vscode/mcp.json`:

**After publishing to PyPI:**

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

## Verifying Installation

After installation, verify that the package is correctly installed:

```bash
python -c "import trino_mcp; print(trino_mcp.__version__)"
```

You should see the version number printed (e.g., `0.1.0`).

## Troubleshooting

### Command not found

If `trino-mcp` command is not found:

1. Ensure the package is installed: `pip list | grep trino-mcp`
2. Check your PATH includes the pip/uv bin directory
3. Try running with Python module: `python -m trino_mcp.server`

### Import errors

If you encounter import errors:

1. Ensure you have Python 3.10 or higher: `python --version`
2. Install the package and its dependencies: `pip install trino-mcp`
3. Check for conflicting packages: `pip list`

### Connection issues

If you can't connect to Trino:

1. Verify Trino is running: `curl http://localhost:8080/v1/status`
2. Check your configuration in `.env` file
3. Ensure network connectivity to Trino server
4. Verify authentication credentials

## Next Steps

- [Configuration](configuration.md) - Configure your Trino connection
- [Quick Start](quickstart.md) - Get started quickly
- [Available Tools](tools.md) - Explore available MCP tools
