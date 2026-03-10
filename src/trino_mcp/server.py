"""Trino MCP Server - Main server implementation."""

import argparse
import asyncio
import logging
import sys
from typing import Annotated, Optional

import sqlglot
from sqlglot.expressions import (
    Insert,
    Update,
    Delete,
    Merge,
    Create,
    Drop,
    Alter,
    Grant,
    Revoke,
    Analyze,
    Refresh,
    Command,
    Describe,
    TruncateTable,
)
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .config import load_config
from .client import QueryTimeoutError, TrinoClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

# Module-level config and client — initialized in main() after CLI args are parsed.
# When imported as a library (e.g. in tests), callers may set these directly.
config = None
client = None
_query_semaphore = None  # Initialized in _init_config()

# Initialize MCP server
mcp = FastMCP(
    name="Trino MCP Server",
    instructions="A simple Model Context Protocol server for Trino query engine with OAuth support.",
)


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

# Mapping from CLI flag dest → environment variable name.
_CLI_TO_ENV = {
    "trino_host": "TRINO_HOST",
    "trino_port": "TRINO_PORT",
    "trino_user": "TRINO_USER",
    "trino_catalog": "TRINO_CATALOG",
    "trino_schema": "TRINO_SCHEMA",
    "trino_http_scheme": "TRINO_HTTP_SCHEME",
    "auth_method": "AUTH_METHOD",
    "trino_password": "TRINO_PASSWORD",
    "azure_scope": "AZURE_SCOPE",
    "azure_client_id": "AZURE_CLIENT_ID",
    "azure_client_secret": "AZURE_CLIENT_SECRET",
    "azure_tenant_id": "AZURE_TENANT_ID",
    "allow_write_queries": "ALLOW_WRITE_QUERIES",
    "custom_watermark": "TRINO_MCP_CUSTOM_WATERMARK",
    "session_properties": "TRINO_SESSION_PROPERTIES",
    "query_timeout_minutes": "QUERY_TIMEOUT_MINUTES",
    "max_concurrent_queries": "MAX_CONCURRENT_QUERIES",
}


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Every flag is optional. When provided, the value is passed as an override
    to ``load_config()``, taking precedence over env vars and ``.env``.
    """
    parser = argparse.ArgumentParser(
        prog="trino-mcp",
        description="Trino MCP Server — Model Context Protocol server for Trino.",
    )

    # Connection
    parser.add_argument("--trino-host", help="Trino host (default: localhost)")
    parser.add_argument("--trino-port", help="Trino port (default: 8080)")
    parser.add_argument("--trino-user", help="Trino user (default: trino)")
    parser.add_argument("--trino-catalog", help="Default catalog")
    parser.add_argument("--trino-schema", help="Default schema")
    parser.add_argument(
        "--trino-http-scheme", help="HTTP scheme: http or https (default: http)"
    )

    # Authentication
    parser.add_argument(
        "--auth-method",
        help="Authentication method: PASSWORD, OAUTH2, AZURE_SPN, or NONE (default: PASSWORD)",
    )
    parser.add_argument("--trino-password", help="Password for PASSWORD auth")
    parser.add_argument("--azure-scope", help="Azure token scope for AZURE_SPN auth")
    parser.add_argument("--azure-client-id", help="Azure client ID for AZURE_SPN auth")
    parser.add_argument(
        "--azure-client-secret", help="Azure client secret for AZURE_SPN auth"
    )
    parser.add_argument(
        "--azure-tenant-id", help="Azure tenant ID for AZURE_SPN auth"
    )

    # Permissions
    parser.add_argument(
        "--allow-write-queries",
        help="Allow write queries: true/false (default: false)",
    )

    # Watermark
    parser.add_argument(
        "--custom-watermark",
        help='JSON object for custom query watermark. Values can be literal strings '
             'or "env:VAR" to resolve from environment variables '
             '(TRINO_MCP_CUSTOM_WATERMARK)',
    )

    # Session properties
    parser.add_argument(
        "--session-properties",
        help='JSON object of Trino session properties '
             '(e.g. \'{"query_max_run_time": "30s"}\') '
             '(TRINO_SESSION_PROPERTIES)',
    )

    # Query timeout
    parser.add_argument(
        "--query-timeout-minutes",
        help="Client-side query timeout in minutes. Queries exceeding this are "
             "cancelled automatically. 0 disables. (default: 5) "
             "(QUERY_TIMEOUT_MINUTES)",
    )

    # Concurrency
    parser.add_argument(
        "--max-concurrent-queries",
        help="Maximum number of concurrent tool calls. Excess calls are rejected "
             "immediately. (default: 1) (MAX_CONCURRENT_QUERIES)",
    )

    return parser


def _cli_args_to_overrides(args: argparse.Namespace) -> dict:
    """Convert non-None CLI values into an overrides dict for ``load_config()``."""
    overrides = {}
    for dest, env_var in _CLI_TO_ENV.items():
        value = getattr(args, dest, None)
        if value is not None:
            overrides[env_var] = value
    return overrides


def _is_read_only_query(query: str) -> bool:
    """Check if a SQL query is read-only using SQL parsing.

    Uses sqlglot to parse the query as Trino SQL and walks the AST to detect
    any write operations (INSERT, UPDATE, DELETE, etc.).

    Note: SELECT statements with functions that have side effects are not detected
    and will be allowed. Users should be aware that SELECT can potentially trigger
    external writes depending on the Trino connectors and functions used.

    Args:
        query: The SQL query to check
    Returns:
        True if the query is read-only, False otherwise
    """
    # Trino write operations (sqlglot maps these to standard expression types)
    WRITE_TYPES = (
        Insert,
        Update,
        Delete,
        Merge,
        Create,
        Drop,
        Alter,
        TruncateTable,
        Grant,
        Revoke,
        Analyze,
        Refresh,
    )

    try:
        # Parse using the Trino dialect
        expr = sqlglot.parse_one(query, read="trino")
    except Exception as e:
        # If parsing fails, treat as non-read-only for safety
        logger.warning(f"Failed to parse query as Trino SQL: {str(e)}")
        return False

    # Describe is read-only
    if isinstance(expr, Describe):
        return True

    # Check if it's a Command statement (SHOW, EXPLAIN, etc.)
    # These are read-only commands but parsed as Command type
    if isinstance(expr, Command):
        # Extract the command text to check
        query_upper = query.strip().upper()

        # EXPLAIN ANALYZE executes the query, so it's NOT read-only
        if query_upper.startswith("EXPLAIN") and "ANALYZE" in query_upper:
            return False

        # SHOW and EXPLAIN (without ANALYZE) are read-only
        # Use exact word matching to avoid false positives like "SHOWING"
        query_words = query_upper.split()
        if query_words and query_words[0] in ("SHOW", "EXPLAIN"):
            return True

        # Other commands are considered write operations for safety
        return False

    # Walk the AST for any write operation
    return not any(isinstance(node, WRITE_TYPES) for node in expr.walk())


def _parse_table_identifier(table: str, catalog: str, schema: str) -> tuple:
    """Parse a table identifier that may be fully qualified.

    Handles cases where the table parameter contains a fully qualified name
    like 'catalog.schema.table' or 'schema.table', extracting the parts and
    using them as overrides when catalog/schema are not already provided.

    Args:
        table: The table name, which may be fully qualified (e.g., 'catalog.schema.table')
        catalog: The catalog name (may be empty)
        schema: The schema name (may be empty)

    Returns:
        A tuple of (catalog, schema, table) with the parsed values
    """
    # Note: This simple split does not handle quoted identifiers containing
    # periods (e.g., "my.catalog"."my.schema"."my.table").
    parts = table.split(".")
    if len(parts) == 3:
        # Fully qualified: catalog.schema.table
        return (catalog or parts[0], schema or parts[1], parts[2])
    elif len(parts) == 2:
        # Partially qualified: schema.table
        return (catalog, schema or parts[0], parts[1])
    else:
        # Just the table name
        return (catalog, schema, table)


def _try_execute_query(query: str, output_file: str = "") -> str:
    """Common function to execute a query.

    Args:
        query: The SQL query to execute
        output_file: If provided, write results directly to this file path.
                     The output format is derived from the file extension:
                     ".csv" writes CSV, ".json" (or any other extension) writes JSON.
                     The data is written server-side and is NOT returned to the caller,
                     preventing the AI from ever receiving the raw values. This enables
                     subsequent processing by other tools without LLM hallucination.

    Returns:
        When output_file is set: a confirmation message with the row count.
        Otherwise: the query results as a JSON string or error message.
    """
    try:
        if output_file:
            row_count = client.execute_query_to_file(query, output_file)
            logger.debug(f"Query results written to {output_file} ({row_count} row(s))")
            return f"Query results written to '{output_file}' ({row_count} row(s))."
        result = client.execute_query_json(query)
        logger.debug("Query executed successfully")
        return result
    except QueryTimeoutError as e:
        logger.warning(f"Query timed out: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}", exc_info=True)
        return f"Error executing query: {str(e)}"


def _concurrency_limit_message() -> str:
    """Return the error message when all concurrent query slots are in use."""
    n = config.max_concurrent_queries if config else 1
    return (
        f"Error: All {n} concurrent query slot(s) are in use. "
        "Please wait for the previous tool call to complete before retrying."
    )


@mcp.tool()
async def list_catalogs() -> str:
    """List all available Trino catalogs."""
    if _query_semaphore is not None and _query_semaphore.locked():
        return _concurrency_limit_message()
    async with _query_semaphore:
        logger.info("Listing catalogs...")
        try:
            catalogs = client.list_catalogs()
            logger.debug(f"Found {len(catalogs)} catalogs")
            return "\n".join(catalogs)
        except QueryTimeoutError as e:
            logger.warning(f"Query timed out: {str(e)}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error listing catalogs: {str(e)}", exc_info=True)
            return f"Error listing catalogs: {str(e)}"


@mcp.tool()
async def list_schemas(catalog: str = Field(description="The catalog name")) -> str:
    """List all schemas in a catalog.

    Args:
        catalog: The name of the catalog to list schemas from
    """
    if _query_semaphore is not None and _query_semaphore.locked():
        return _concurrency_limit_message()
    async with _query_semaphore:
        logger.info(f"Listing schemas for catalog: {catalog}")
        try:
            schemas = client.list_schemas(catalog)
            logger.debug(f"Found {len(schemas)} schemas")
            return "\n".join(schemas)
        except QueryTimeoutError as e:
            logger.warning(f"Query timed out: {str(e)}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error listing schemas: {str(e)}", exc_info=True)
            return f"Error listing schemas: {str(e)}"


@mcp.tool()
async def list_tables(
    catalog: str = Field(description="The catalog name"),
    schema: str = Field(description="The schema name"),
) -> str:
    """List all tables in a schema.

    Args:
        catalog: The name of the catalog
        schema: The name of the schema
    """
    if _query_semaphore is not None and _query_semaphore.locked():
        return _concurrency_limit_message()
    async with _query_semaphore:
        logger.info(f"Listing tables for {catalog}.{schema}")
        try:
            tables = client.list_tables(catalog, schema)
            logger.debug(f"Found {len(tables)} tables")
            return "\n".join(tables)
        except QueryTimeoutError as e:
            logger.warning(f"Query timed out: {str(e)}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}", exc_info=True)
            return f"Error listing tables: {str(e)}"


@mcp.tool()
async def describe_table(
    table: str = Field(
        description="The table name (e.g. 'my_table'). Preferably just the table name; catalog and schema should be passed as separate parameters. Fully qualified names like 'catalog.schema.table' are also accepted for convenience."
    ),
    catalog: str = Field(
        description="The catalog name (e.g. 'my_catalog')", default=""
    ),
    schema: str = Field(description="The schema name (e.g. 'my_schema')", default=""),
) -> str:
    """Describe the structure of a table (columns, types, etc).

    Args:
        table: The table name (e.g. 'my_table'). Preferably just the table name; catalog and schema should be passed as separate parameters. Fully qualified names like 'catalog.schema.table' are also accepted.
        catalog: The catalog name (optional if default is configured)
        schema: The schema name (optional if default is configured)
    """
    if _query_semaphore is not None and _query_semaphore.locked():
        return _concurrency_limit_message()
    async with _query_semaphore:
        logger.info(f"Describing table: {catalog}.{schema}.{table}")
        try:
            cat, sch, tbl = _parse_table_identifier(table, catalog, schema)
            result = client.describe_table(cat, sch, tbl)
            logger.debug(f"Table description retrieved successfully")
            return result
        except QueryTimeoutError as e:
            logger.warning(f"Query timed out: {str(e)}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error describing table: {str(e)}", exc_info=True)
            return f"Error describing table: {str(e)}"


@mcp.tool()
async def execute_query_read_only(
    query: str = Field(description="The SQL query to execute (read-only)"),
    output_file: Annotated[
        str,
        Field(
            description="File path to write results to. Format is derived from the file extension: '.csv' for CSV, '.json' (or others) for JSON. When set, results are written directly to disk and are NOT returned to the AI, preventing hallucinated values and enabling subsequent processing by other tools."
        ),
    ] = "",
) -> str:
    """Execute a read-only SQL query and return the results.

    This tool is designed for read-only queries (SELECT, SHOW, DESCRIBE, EXPLAIN, etc.).
    It validates that the query is read-only before execution.

    When output_file is provided, results are written directly to disk and only a
    confirmation message is returned. This prevents raw data from passing through
    the AI, avoiding hallucination when processing large result sets. The output
    format (JSON or CSV) is derived from the file extension.

    Args:
        query: The SQL query to execute (must be read-only)
        output_file: File path to write results to. Extension determines format
                     (.csv → CSV, .json or others → JSON). Results are NOT returned
                     to the AI, enabling reliable downstream processing.
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
    if _query_semaphore is not None and _query_semaphore.locked():
        return _concurrency_limit_message()
    async with _query_semaphore:
        return _try_execute_query(query, output_file=output_file)


@mcp.tool()
async def execute_query(
    query: str = Field(description="The SQL query to execute"),
    output_file: Annotated[
        str,
        Field(
            description="File path to write results to. Format is derived from the file extension: '.csv' for CSV, '.json' (or others) for JSON. When set, results are written directly to disk and are NOT returned to the AI, preventing hallucinated values and enabling subsequent processing by other tools."
        ),
    ] = "",
) -> str:
    """Execute a SQL query and return the results.

    This tool can execute any SQL query including write operations (INSERT, UPDATE, DELETE, etc.).
    By default, write operations are disabled for security. Set ALLOW_WRITE_QUERIES=true to enable.

    When output_file is provided, results are written directly to disk and only a
    confirmation message is returned. This prevents raw data from passing through
    the AI, avoiding hallucination when processing large result sets. The output
    format (JSON or CSV) is derived from the file extension.

    Args:
        query: The SQL query to execute
        output_file: File path to write results to. Extension determines format
                     (.csv → CSV, .json or others → JSON). Results are NOT returned
                     to the AI, enabling reliable downstream processing.
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
    if _query_semaphore is not None and _query_semaphore.locked():
        return _concurrency_limit_message()
    async with _query_semaphore:
        return _try_execute_query(query, output_file=output_file)


@mcp.tool()
async def show_create_table(
    table: str = Field(
        description="The table name (e.g. 'my_table'). Preferably just the table name; catalog and schema should be passed as separate parameters. Fully qualified names like 'catalog.schema.table' are also accepted for convenience."
    ),
    catalog: str = Field(
        description="The catalog name (e.g. 'my_catalog')", default=""
    ),
    schema: str = Field(description="The schema name (e.g. 'my_schema')", default=""),
) -> str:
    """Show the CREATE TABLE statement for a table.

    Args:
        table: The table name (e.g. 'my_table'). Preferably just the table name; catalog and schema should be passed as separate parameters. Fully qualified names like 'catalog.schema.table' are also accepted.
        catalog: The catalog name (optional if default is configured)
        schema: The schema name (optional if default is configured)
    """
    logger.info(f"Getting CREATE TABLE for: {catalog}.{schema}.{table}")
    try:
        cat, sch, tbl = _parse_table_identifier(table, catalog, schema)
        result = client.show_create_table(cat, sch, tbl)
        logger.debug(f"CREATE TABLE retrieved successfully")
        return result
    except Exception as e:
        logger.error(f"Error showing CREATE TABLE: {str(e)}", exc_info=True)
        return f"Error showing CREATE TABLE: {str(e)}"


@mcp.tool()
async def get_table_stats(
    table: str = Field(
        description="The table name (e.g. 'my_table'). Preferably just the table name; catalog and schema should be passed as separate parameters. Fully qualified names like 'catalog.schema.table' are also accepted for convenience."
    ),
    catalog: str = Field(
        description="The catalog name (e.g. 'my_catalog')", default=""
    ),
    schema: str = Field(description="The schema name (e.g. 'my_schema')", default=""),
) -> str:
    """Get statistics for a table.

    Args:
        table: The table name (e.g. 'my_table'). Preferably just the table name; catalog and schema should be passed as separate parameters. Fully qualified names like 'catalog.schema.table' are also accepted.
        catalog: The catalog name (optional if default is configured)
        schema: The schema name (optional if default is configured)
    """
    if _query_semaphore is not None and _query_semaphore.locked():
        return _concurrency_limit_message()
    async with _query_semaphore:
        logger.info(f"Getting table stats for: {catalog}.{schema}.{table}")
        try:
            cat, sch, tbl = _parse_table_identifier(table, catalog, schema)
            result = client.get_table_stats(cat, sch, tbl)
            logger.debug(f"Table stats retrieved successfully")
            return result
        except QueryTimeoutError as e:
            logger.warning(f"Query timed out: {str(e)}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error getting table stats: {str(e)}", exc_info=True)
            return f"Error getting table stats: {str(e)}"


def _init_config(overrides: Optional[dict] = None) -> None:
    """Initialise the global ``config`` and ``client``.

    Args:
        overrides: Optional dict of env-var-name → value that takes
                   precedence over environment variables and ``.env``.
    """
    global config, client, _query_semaphore
    logger.info("Loading Trino configuration...")
    config = load_config(overrides=overrides)
    logger.info(f"Connected to Trino at {config.host}:{config.port}")
    client = TrinoClient(config)

    # Concurrency gate — limits how many tool calls can run at the same time.
    _query_semaphore = asyncio.Semaphore(config.max_concurrent_queries)

    # Update MCP instructions so agents know the constraints.
    mcp._mcp_server.instructions = (
        "A Model Context Protocol server for Trino query engine. "
        "IMPORTANT CONSTRAINTS — read before calling tools:\n"
        f"• Concurrency limit: only {config.max_concurrent_queries} tool call(s) may run at a time. "
        "If you receive a concurrency-limit error, wait for the previous call to finish and retry.\n"
        f"• Query timeout: queries that run longer than {config.query_timeout_minutes:g} minute(s) are "
        "automatically cancelled. Write efficient queries — avoid SELECT * on large tables and add "
        "appropriate filters (WHERE, LIMIT).\n"
        "• Issue tool calls one at a time and wait for each result before issuing the next call."
    )


def main():
    """Main entry point for the server."""
    global config, client

    # Parse CLI arguments into an overrides dict (no env mutation).
    parser = _build_arg_parser()
    args = parser.parse_args()
    overrides = _cli_args_to_overrides(args)

    _init_config(overrides)

    logger.info("Starting Trino MCP Server...")
    mcp.run()
    logger.info("Trino MCP Server stopped")


if __name__ == "__main__":
    main()
