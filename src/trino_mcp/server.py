"""Trino MCP Server - Main server implementation."""

import logging
import sys
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .config import load_config
from .client import TrinoClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

# Initialize configuration and client
logger.info("Loading Trino configuration...")
config = load_config()
logger.info(f"Connected to Trino at {config.host}:{config.port}")
client = TrinoClient(config)

# Initialize MCP server
mcp = FastMCP(
    name="Trino MCP Server",
    instructions="A simple Model Context Protocol server for Trino query engine with OAuth support.",
)


def _is_read_only_query(query: str) -> bool:
    """Check if a SQL query is read-only using SQL parsing.
    
    Args:
        query: The SQL query to check
        
    Returns:
        True if the query is read-only, False otherwise
    """
    # Parse the SQL query
    parsed = sqlparse.parse(query)
    if not parsed:
        return False
    
    # Check the first statement
    statement = parsed[0]
    
    # Get the first meaningful token (skip whitespace and comments)
    first_token = None
    for token in statement.tokens:
        if token.ttype not in (sqlparse.tokens.Whitespace, sqlparse.tokens.Comment.Single, 
                               sqlparse.tokens.Comment.Multiline):
            first_token = token
            break
    
    if not first_token:
        return False
    
    # Check if it's a read-only statement type
    # Read-only: SELECT, SHOW, DESCRIBE, EXPLAIN, WITH (for CTEs with SELECT)
    # Write: INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, TRUNCATE, MERGE, GRANT, REVOKE, etc.
    token_value = first_token.value.upper()
    
    read_only_keywords = {'SELECT', 'SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN', 'WITH'}
    write_keywords = {'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 
                      'TRUNCATE', 'MERGE', 'REPLACE', 'GRANT', 'REVOKE', 'CALL'}
    
    # Check for write operations
    if any(token_value.startswith(keyword) for keyword in write_keywords):
        return False
    
    # Check for read-only operations
    if any(token_value.startswith(keyword) for keyword in read_only_keywords):
        return True
    
    # Default to not read-only for safety
    return False


def _try_execute_query(query: str) -> str:
    """Common function to execute a query.
    
    Args:
        query: The SQL query to execute
        
    Returns:
        The query results as a JSON string or error message
    """
    try:
        result = client.execute_query(query)
        logger.debug(f"Query executed successfully")
        return result
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}", exc_info=True)
        return f"Error executing query: {str(e)}"


@mcp.tool()
def list_catalogs() -> str:
    """List all available Trino catalogs."""
    logger.info("Listing catalogs...")
    try:
        catalogs = client.list_catalogs()
        logger.debug(f"Found {len(catalogs)} catalogs")
        return "\n".join(catalogs)
    except Exception as e:
        logger.error(f"Error listing catalogs: {str(e)}", exc_info=True)
        return f"Error listing catalogs: {str(e)}"


@mcp.tool()
def list_schemas(catalog: str = Field(description="The catalog name")) -> str:
    """List all schemas in a catalog.

    Args:
        catalog: The name of the catalog to list schemas from
    """
    logger.info(f"Listing schemas for catalog: {catalog}")
    try:
        schemas = client.list_schemas(catalog)
        logger.debug(f"Found {len(schemas)} schemas")
        return "\n".join(schemas)
    except Exception as e:
        logger.error(f"Error listing schemas: {str(e)}", exc_info=True)
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
    logger.info(f"Listing tables for {catalog}.{schema}")
    try:
        tables = client.list_tables(catalog, schema)
        logger.debug(f"Found {len(tables)} tables")
        return "\n".join(tables)
    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}", exc_info=True)
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
    logger.info(f"Describing table: {catalog}.{schema}.{table}")
    try:
        cat = catalog if catalog else ""
        sch = schema if schema else ""
        result = client.describe_table(cat, sch, table)
        logger.debug(f"Table description retrieved successfully")
        return result
    except Exception as e:
        logger.error(f"Error describing table: {str(e)}", exc_info=True)
        return f"Error describing table: {str(e)}"


@mcp.tool()
def execute_query_read_only(query: str = Field(description="The SQL query to execute (read-only)")) -> str:
    """Execute a read-only SQL query and return the results.
    
    This tool is designed for read-only queries (SELECT, SHOW, DESCRIBE, EXPLAIN, etc.).
    It validates that the query is read-only before execution.

    Args:
        query: The SQL query to execute (must be read-only)
    """
    logger.info(f"Executing read-only query: {query[:100]}...")
    
    # Check if the query is actually read-only
    if not _is_read_only_query(query):
        logger.warning(f"Non-read-only query blocked: {query[:100]}...")
        return (
            "Error: This query does not appear to be read-only. "
            "The execute_query_read_only tool only accepts SELECT, SHOW, DESCRIBE, and EXPLAIN queries. "
            "If you need to execute write operations (INSERT, UPDATE, DELETE, CREATE, DROP, etc.), "
            "use the 'execute_query' tool instead (requires ALLOW_WRITE_QUERIES=true)."
        )
    
    # Execute the query using the common function
    return _try_execute_query(query)


@mcp.tool()
def execute_query(query: str = Field(description="The SQL query to execute")) -> str:
    """Execute a SQL query and return the results.
    
    This tool can execute any SQL query including write operations (INSERT, UPDATE, DELETE, etc.).
    By default, write operations are disabled for security. Set ALLOW_WRITE_QUERIES=true to enable.

    Args:
        query: The SQL query to execute
    """
    logger.info(f"Executing query: {query[:100]}...")
    
    # Check if write queries are allowed
    if not config.allow_write_queries:
        logger.warning(f"Write queries are disabled. Query blocked: {query[:100]}...")
        return (
            "Error: Write queries are disabled by default for security. "
            "This tool can potentially execute write operations (INSERT, UPDATE, DELETE, CREATE, DROP, etc.). "
            "If you only need to read data, please use the 'execute_query_read_only' tool instead. "
            "To enable write queries, set ALLOW_WRITE_QUERIES=true in your environment configuration."
        )
    
    # Execute the query using the common function
    return _try_execute_query(query)


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
    logger.info(f"Getting CREATE TABLE for: {catalog}.{schema}.{table}")
    try:
        cat = catalog if catalog else ""
        sch = schema if schema else ""
        result = client.show_create_table(cat, sch, table)
        logger.debug(f"CREATE TABLE retrieved successfully")
        return result
    except Exception as e:
        logger.error(f"Error showing CREATE TABLE: {str(e)}", exc_info=True)
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
    logger.info(f"Getting table stats for: {catalog}.{schema}.{table}")
    try:
        cat = catalog if catalog else ""
        sch = schema if schema else ""
        result = client.get_table_stats(cat, sch, table)
        logger.debug(f"Table stats retrieved successfully")
        return result
    except Exception as e:
        logger.error(f"Error getting table stats: {str(e)}", exc_info=True)
        return f"Error getting table stats: {str(e)}"


def main():
    """Main entry point for the server."""
    logger.info("Starting Trino MCP Server...")
    mcp.run()
    logger.info("Trino MCP Server stopped")


if __name__ == "__main__":
    main()
