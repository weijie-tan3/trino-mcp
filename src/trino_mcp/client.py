"""Trino client for executing queries."""

import json
from typing import Any, Dict, List, Union

import trino
from trino.dbapi import Connection, Cursor

from . import __version__
from .config import TrinoConfig


class TrinoClient:
    """Client for interacting with Trino."""

    def __init__(self, config: TrinoConfig):
        """Initialize the Trino client."""
        self.config = config
        self.connection = self._create_connection()

    def _create_connection(self) -> Connection:
        """Create a new Trino connection."""
        return trino.dbapi.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            catalog=self.config.catalog,
            schema=self.config.schema,
            http_scheme=self.config.http_scheme,
            auth=self.config.auth,
            **(self.config.additional_kwargs or {}),
        )

    def _add_watermark(self, query: str) -> str:
        """Add watermark comment to the query.

        Args:
            query: The SQL query to add watermark to

        Returns:
            The query with watermark comment prepended
        """
        watermark = f"-- {self.config.user}, trino-mcp v{__version__} --\n"
        return watermark + query

    def execute_query_raw(self, query: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Execute a SQL query and return results as Python data structures.
        
        This method returns native Python data structures instead of JSON strings,
        making it ideal for programmatic use when using trino-mcp as a library.
        
        Args:
            query: The SQL query to execute
            
        Returns:
            List of dictionaries for queries with results (SELECT, SHOW, etc.)
            or a status dictionary for queries without results (DDL/DML)
        """
        cursor: Cursor = self.connection.cursor()
        watermarked_query = self._add_watermark(query)
        cursor.execute(watermarked_query)

        if cursor.description:
            # Query returned results
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            # Query executed successfully but returned no output
            # (e.g., INSERT, UPDATE, DELETE, CREATE, DROP statements)
            return {"status": "success", "message": "Query executed successfully without output."}

    def execute_query(self, query: str) -> str:
        """Execute a SQL query and return results as JSON string.
        
        Note: This method returns a JSON string for backward compatibility with MCP server.
        For programmatic use as a library, use execute_query_raw() to get native Python data structures.
        """
        result = self.execute_query_raw(query)
        return json.dumps(result, default=str, indent=2)

    def list_catalogs(self) -> List[str]:
        """List all available catalogs."""
        data = self.execute_query_raw("SHOW CATALOGS")
        if isinstance(data, dict):
            # Query didn't return results (unexpected for SHOW CATALOGS)
            raise RuntimeError(
                f"Expected list of results from SHOW CATALOGS, but got status dict: {data}"
            )
        return [row["Catalog"] for row in data]

    def list_schemas(self, catalog: str) -> List[str]:
        """List all schemas in a catalog."""
        catalog_name = catalog or self.config.catalog
        if not catalog_name:
            raise ValueError("Catalog must be specified")

        data = self.execute_query_raw(f"SHOW SCHEMAS FROM {catalog_name}")
        if isinstance(data, dict):
            # Query didn't return results (unexpected for SHOW SCHEMAS)
            raise RuntimeError(
                f"Expected list of results from SHOW SCHEMAS, but got status dict: {data}"
            )
        return [row["Schema"] for row in data]

    def list_tables(self, catalog: str, schema: str) -> List[str]:
        """List all tables in a schema."""
        catalog_name = catalog or self.config.catalog
        schema_name = schema or self.config.schema

        if not catalog_name or not schema_name:
            raise ValueError("Both catalog and schema must be specified")

        data = self.execute_query_raw(f"SHOW TABLES FROM {catalog_name}.{schema_name}")
        if isinstance(data, dict):
            # Query didn't return results (unexpected for SHOW TABLES)
            raise RuntimeError(
                f"Expected list of results from SHOW TABLES, but got status dict: {data}"
            )
        return [row["Table"] for row in data]

    def describe_table(self, catalog: str, schema: str, table: str) -> str:
        """Describe the structure of a table."""
        catalog_name = catalog or self.config.catalog
        schema_name = schema or self.config.schema

        if not catalog_name or not schema_name:
            raise ValueError("Both catalog and schema must be specified")

        return self.execute_query(f"DESCRIBE {catalog_name}.{schema_name}.{table}")

    def show_create_table(self, catalog: str, schema: str, table: str) -> str:
        """Show the CREATE TABLE statement for a table."""
        catalog_name = catalog or self.config.catalog
        schema_name = schema or self.config.schema

        if not catalog_name or not schema_name:
            raise ValueError("Both catalog and schema must be specified")

        data = self.execute_query_raw(
            f"SHOW CREATE TABLE {catalog_name}.{schema_name}.{table}"
        )
        if isinstance(data, dict):
            # Query didn't return results (unexpected for SHOW CREATE TABLE)
            raise RuntimeError(
                f"Expected list of results from SHOW CREATE TABLE, but got status dict: {data}"
            )
        return data[0]["Create Table"] if data else ""

    def get_table_stats(self, catalog: str, schema: str, table: str) -> str:
        """Get statistics for a table."""
        catalog_name = catalog or self.config.catalog
        schema_name = schema or self.config.schema

        if not catalog_name or not schema_name:
            raise ValueError("Both catalog and schema must be specified")

        return self.execute_query(
            f"SHOW STATS FOR {catalog_name}.{schema_name}.{table}"
        )
