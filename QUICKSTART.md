# Quick Start Guide

This guide will help you get started with the Trino MCP Server in minutes.

## Prerequisites

- Python 3.11 or higher
- Access to a Trino server
- `uv` or `uvx` installed (recommended) or `pip`

## Step 1: Setup

### Clone or Download

```bash
git clone <your-repo-url>
cd trino-mcp
```

### Create Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your Trino connection details:

```bash
TRINO_HOST=your-trino-host
TRINO_PORT=8080
TRINO_USER=your-username
TRINO_PASSWORD=your-password  # Optional for basic auth
```

## Step 2: Run with uvx (Easiest)

### From PyPI (once published)
```bash
# Run directly from PyPI without installation
uvx trino-mcp
```

### From Local Directory
```bash
# Run directly without installation
uvx --from . trino-mcp
```

The server will start and listen for MCP connections via stdio.

## Step 3: Test with Claude Desktop

### From PyPI (once published)
1. Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

### From Local Directory
1. Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "trino": {
      "command": "uvx",
      "args": ["--from", "/full/path/to/trino-mcp", "trino-mcp"],
      "env": {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino"
      }
    }
  }
}
```

2. Restart Claude Desktop

3. You should now see Trino tools available in Claude!

## Step 4: Try Some Commands

In Claude, try asking:

- "List all available Trino catalogs"
- "Show me the schemas in the [catalog_name] catalog"
- "What tables are in [catalog].[schema]?"
- "Describe the table [catalog].[schema].[table]"
- "Execute this query: SELECT * FROM [catalog].[schema].[table] LIMIT 10"

## Alternative: Run with uv

```bash
# Install
uv pip install .

# Run
trino-mcp
```

## Alternative: Development Mode

```bash
# Install in editable mode
uv pip install -e .

# Run
python -m trino_mcp.server
```

## Testing Without Claude

You can test the client directly with Python:

```bash
python examples/basic_usage.py
```

## Troubleshooting

### Connection Issues

1. Verify your Trino server is running: `curl http://your-trino-host:8080/v1/info`
2. Check your credentials are correct
3. Ensure network connectivity to Trino server

### uvx Not Found

Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Module Not Found

Make sure you're in the project directory or have installed the package.

## Next Steps

- Check out the full [README.md](README.md) for detailed documentation
- Explore the [examples](examples/) directory
- Read about [Trino](https://trino.io/docs/) features

## Getting Help

- Open an issue on GitHub
- Check Trino documentation: https://trino.io/docs/
- Check MCP documentation: https://modelcontextprotocol.io/
