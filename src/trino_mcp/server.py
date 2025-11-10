"""Trino MCP Server - Main server implementation."""

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .config import load_config
from .client import TrinoClient

# Initialize configuration and client
config = load_config()
client = TrinoClient(config)

# Initialize MCP server
mcp = FastMCP(
    name="Trino MCP Server",
    instructions="A simple Model Context Protocol server for Trino query engine with OAuth support.",
)


@mcp.tool()
def list_catalogs() -> str:
    """List all available Trino catalogs."""
    try:
        catalogs = client.list_catalogs()
        return "\n".join(catalogs)
    except Exception as e:
        return f"Error listing catalogs: {str(e)}"


@mcp.tool()
def list_schemas(catalog: str = Field(description="The catalog name")) -> str:
    """List all schemas in a catalog.

    Args:
        catalog: The name of the catalog to list schemas from
    """
    try:
        schemas = client.list_schemas(catalog)
        return "\n".join(schemas)
    except Exception as e:
        return f"Error listing schemas: {str(e)}"


@mcp.tool()
def list_tables(
    catalog: str = Field(description="The catalog name"),
    schema: str = Field(description="The schema name"),
) -> str:
    """List all tables in a schema.

    Args:
        catalog: The name of the catalog
        schema: The name of the schema
    """
    try:
        tables = client.list_tables(catalog, schema)
        return "\n".join(tables)
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool()
def describe_table(
    table: str = Field(description="The table name"),
    catalog: str = Field(description="The catalog name", default=""),
    schema: str = Field(description="The schema name", default=""),
) -> str:
    """Describe the structure of a table (columns, types, etc).

    Args:
        table: The name of the table
        catalog: The catalog name (optional if default is configured)
        schema: The schema name (optional if default is configured)
    """
    try:
        cat = catalog if catalog else ""
        sch = schema if schema else ""
        return client.describe_table(cat, sch, table)
    except Exception as e:
        return f"Error describing table: {str(e)}"


@mcp.tool()
def execute_query(query: str = Field(description="The SQL query to execute")) -> str:
    """Execute a SQL query and return the results.

    Args:
        query: The SQL query to execute
    """
    try:
        return client.execute_query(query)
    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.tool()
def show_create_table(
    table: str = Field(description="The table name"),
    catalog: str = Field(description="The catalog name", default=""),
    schema: str = Field(description="The schema name", default=""),
) -> str:
    """Show the CREATE TABLE statement for a table.

    Args:
        table: The name of the table
        catalog: The catalog name (optional if default is configured)
        schema: The schema name (optional if default is configured)
    """
    try:
        cat = catalog if catalog else ""
        sch = schema if schema else ""
        return client.show_create_table(cat, sch, table)
    except Exception as e:
        return f"Error showing CREATE TABLE: {str(e)}"


@mcp.tool()
def get_table_stats(
    table: str = Field(description="The table name"),
    catalog: str = Field(description="The catalog name", default=""),
    schema: str = Field(description="The schema name", default=""),
) -> str:
    """Get statistics for a table.

    Args:
        table: The name of the table
        catalog: The catalog name (optional if default is configured)
        schema: The schema name (optional if default is configured)
    """
    try:
        cat = catalog if catalog else ""
        sch = schema if schema else ""
        return client.get_table_stats(cat, sch, table)
    except Exception as e:
        return f"Error getting table stats: {str(e)}"


def main():
    """Main entry point for the server."""
    mcp.run()


if __name__ == "__main__":
    main()
