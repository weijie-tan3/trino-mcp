# Quick Start

Get up and running with Trino MCP Server in minutes!

## Prerequisites

- Python 3.10 or higher
- A running Trino server
- Trino connection credentials

## Step 1: Install

=== "uvx (Recommended)"

    ```bash
    uvx trino-mcp
    ```

=== "uv"

    ```bash
    uv pip install trino-mcp
    trino-mcp
    ```

=== "pip"

    ```bash
    pip install trino-mcp
    trino-mcp
    ```

## Step 2: Configure

Create a `.env` file in your working directory:

```bash
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=trino
TRINO_HTTP_SCHEME=http
```

For production with authentication:

```bash
TRINO_HOST=trino.example.com
TRINO_PORT=8443
TRINO_USER=your_username
TRINO_PASSWORD=your_password
TRINO_HTTP_SCHEME=https
```

## Step 3: Run

Start the MCP server:

```bash
trino-mcp
```

You should see output like:

```
2024-01-15 10:00:00 - trino_mcp.server - INFO - Loading Trino configuration...
2024-01-15 10:00:00 - trino_mcp.server - INFO - Connected to Trino at localhost:8080
```

## Step 4: Connect from MCP Client

### Using Claude Desktop

Edit your Claude Desktop configuration:

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

Restart Claude Desktop. You should now see "Trino MCP Server" in your available tools!

## Step 5: Try It Out

Once connected through an MCP client, try these queries:

### List Catalogs

```
What catalogs are available in Trino?
```

The server will use the `list_catalogs` tool to show all available catalogs.

### Explore a Schema

```
Show me the schemas in the hive catalog
```

The server will use the `list_schemas` tool with the hive catalog.

### Query a Table

```
What are the columns in the customers table in hive.default?
```

The server will use the `describe_table` tool to show the table structure.

### Execute SQL

```
Show me the first 10 rows from hive.default.customers
```

The server will use the `execute_query` tool to run:
```sql
SELECT * FROM hive.default.customers LIMIT 10
```

## Common Tasks

### List All Tables in a Schema

Ask your MCP client:
```
List all tables in the production schema of the hive catalog
```

### Get Table Statistics

Ask your MCP client:
```
Show me statistics for the orders table in hive.production
```

### Execute Custom SQL

Ask your MCP client:
```
Execute this SQL: SELECT count(*) FROM hive.production.orders WHERE order_date >= DATE '2024-01-01'
```

## Example Workflow

Here's a complete example workflow:

1. **Discover available data:**
   ```
   What catalogs do we have?
   ```

2. **Explore a catalog:**
   ```
   Show me all schemas in the hive catalog
   ```

3. **Find tables:**
   ```
   What tables are in hive.production?
   ```

4. **Understand structure:**
   ```
   Describe the structure of hive.production.customers
   ```

5. **Query data:**
   ```
   Show me 5 example rows from hive.production.customers
   ```

6. **Analyze data:**
   ```
   Count how many customers we have by country in hive.production.customers
   ```

## Troubleshooting

### Server Won't Start

1. Check Python version: `python --version` (must be 3.10+)
2. Verify installation: `pip list | grep trino-mcp`
3. Check Trino connectivity: `curl http://localhost:8080/v1/status`

### Can't Connect from MCP Client

1. Ensure server is running
2. Check MCP client configuration file syntax
3. Verify environment variables are set correctly
4. Restart the MCP client application

### Query Errors

1. Verify you have permission to access the catalog/schema/table
2. Check SQL syntax
3. Review Trino server logs
4. Ensure table names are fully qualified (catalog.schema.table)

## Next Steps

- [Configuration](configuration.md) - Advanced configuration options
- [Available Tools](tools.md) - Complete tool reference
- [Authentication](authentication.md) - Set up secure authentication
- [Examples](examples.md) - More usage examples
