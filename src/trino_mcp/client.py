"""Trino client for executing queries."""

import csv
import json
import os
from typing import Any, Dict, List, Optional, Tuple, Union

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
        watermark_data: dict = {
            "trino_mcp_version": __version__,
            "user": self.config.user,
        }
        if self.config.custom_watermark:
            watermark_data.update(sorted(self.config.custom_watermark.items()))
        watermark = f"-- {json.dumps(watermark_data)} --\n"
        return watermark + query

    def _execute_cursor(
        self, query: str
    ) -> Tuple[Optional[List[str]], Optional[List[tuple]]]:
        """Execute a query and return the raw cursor data.

        This is the lowest-level execution method. It returns column names and
        raw row tuples directly from the cursor, avoiding any intermediate
        conversion.

        Args:
            query: The SQL query to execute

        Returns:
            A tuple of (columns, rows) for queries with results, or (None, None)
            for DDL/DML statements that produce no output.
        """
        cursor: Cursor = self.connection.cursor()
        watermarked_query = self._add_watermark(query)
        cursor.execute(watermarked_query)

        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return columns, rows
        return None, None

    def execute_query(self, query: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Execute a SQL query and return results as Python data structures.

        Args:
            query: The SQL query to execute

        Returns:
            List of dictionaries for queries with results (SELECT, SHOW, etc.)
            or a status dictionary for queries without results (DDL/DML)
        """
        columns, rows = self._execute_cursor(query)
        if columns is not None and rows is not None:
            return [dict(zip(columns, row)) for row in rows]
        return {
            "status": "success",
            "message": "Query executed successfully without output.",
        }

    def execute_query_json(self, query: str) -> str:
        """Execute a SQL query and return results as a JSON string.

        Args:
            query: The SQL query to execute

        Returns:
            JSON string with 2-space indentation.

        Note: For programmatic use as a library, use execute_query() to get native Python data structures.
              To write results directly to a file (CSV or JSON), use execute_query_to_file().
        """
        result = self.execute_query(query)
        return json.dumps(result, default=str, indent=2)

    def execute_query_to_file(self, query: str, output_file: str) -> int:
        """Execute a query and write results directly to a file.

        The output format is derived from the file extension:
        - ``.csv`` → CSV with a header row (written directly from cursor data,
          no intermediate dict conversion).
        - ``.json`` (or any other extension) → JSON with 2-space indentation.

        This avoids the overhead of zipping columns and rows into dicts when
        CSV output is requested.

        Args:
            query: The SQL query to execute
            output_file: Destination file path. Extension determines format.

        Returns:
            The number of rows written.
        """
        columns, rows = self._execute_cursor(query)
        ext = os.path.splitext(output_file)[1].lower()

        if columns is not None and rows is not None:
            if ext == ".csv":
                with open(output_file, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(rows)
            else:
                data = [dict(zip(columns, row)) for row in rows]
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, default=str, indent=2)
            return len(rows)
        else:
            status = {
                "status": "success",
                "message": "Query executed successfully without output.",
            }
            if ext == ".csv":
                with open(output_file, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(status.keys())
                    writer.writerow(status.values())
            else:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(status, f, default=str, indent=2)
            return 1

    def list_catalogs(self) -> List[str]:
        """List all available catalogs."""
        data = self.execute_query("SHOW CATALOGS")
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

        data = self.execute_query(f"SHOW SCHEMAS FROM {catalog_name}")
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

        data = self.execute_query(f"SHOW TABLES FROM {catalog_name}.{schema_name}")
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

        return self.execute_query_json(f"DESCRIBE {catalog_name}.{schema_name}.{table}")

    def show_create_table(self, catalog: str, schema: str, table: str) -> str:
        """Show the CREATE TABLE statement for a table."""
        catalog_name = catalog or self.config.catalog
        schema_name = schema or self.config.schema

        if not catalog_name or not schema_name:
            raise ValueError("Both catalog and schema must be specified")

        data = self.execute_query(
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

        return self.execute_query_json(
            f"SHOW STATS FOR {catalog_name}.{schema_name}.{table}"
        )
