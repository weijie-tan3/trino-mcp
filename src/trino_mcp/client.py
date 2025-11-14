"""Trino client for executing queries."""

import json
import re
from typing import List

import trino
from trino.dbapi import Connection, Cursor

from .config import TrinoConfig


class TrinoClient:
    """Client for interacting with Trino."""

    # SQL keywords that indicate write operations
    WRITE_KEYWORDS = {
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "MERGE",
        "REPLACE",
        "GRANT",
        "REVOKE",
        "CALL",
    }

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

    def _is_write_query(self, query: str) -> bool:
        """Check if a query contains write operations.

        Args:
            query: SQL query to check

        Returns:
            True if the query contains write operations, False otherwise
        """
        # Normalize the query: remove comments and extra whitespace
        # Remove single-line comments (-- style)
        query_normalized = re.sub(r"--[^\n]*", "", query)
        # Remove multi-line comments (/* */ style)
        query_normalized = re.sub(r"/\*.*?\*/", "", query_normalized, flags=re.DOTALL)
        # Normalize whitespace
        query_normalized = " ".join(query_normalized.split()).upper()

        # Check for read-only patterns that might contain write keywords
        # These should NOT be flagged as write queries
        read_only_patterns = [
            r"\bSHOW\s+CREATE\s+TABLE\b",
            r"\bSHOW\s+CREATE\s+VIEW\b",
            r"\bSHOW\s+CREATE\s+SCHEMA\b",
        ]
        
        for pattern in read_only_patterns:
            if re.search(pattern, query_normalized):
                return False

        # Check if query starts with any write keyword
        for keyword in self.WRITE_KEYWORDS:
            # Use word boundary to avoid false positives (e.g., INSERTED as column name)
            if re.search(rf"\b{keyword}\b", query_normalized):
                return True

        return False

    def execute_query(self, query: str) -> str:
        """Execute a SQL query and return results as JSON string.

        Args:
            query: SQL query to execute

        Returns:
            JSON string with query results

        Raises:
            PermissionError: If write queries are disabled and query contains write operations
        """
        # Check if write queries are allowed
        if not self.config.allow_write_queries and self._is_write_query(query):
            raise PermissionError(
                "Write queries are disabled. Set ALLOW_WRITE_QUERIES=true to enable write operations. "
                "Detected write operation in query."
            )

        cursor: Cursor = self.connection.cursor()
        cursor.execute(query)

        if cursor.description:
            # Query returned results
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            return json.dumps(results, default=str, indent=2)
        else:
            # Query executed successfully without results
            return json.dumps(
                {"status": "success", "message": "Query executed successfully"}
            )

    def list_catalogs(self) -> List[str]:
        """List all available catalogs."""
        result = self.execute_query("SHOW CATALOGS")
        data = json.loads(result)
        return [row["Catalog"] for row in data]

    def list_schemas(self, catalog: str) -> List[str]:
        """List all schemas in a catalog."""
        catalog_name = catalog or self.config.catalog
        if not catalog_name:
            raise ValueError("Catalog must be specified")

        result = self.execute_query(f"SHOW SCHEMAS FROM {catalog_name}")
        data = json.loads(result)
        return [row["Schema"] for row in data]

    def list_tables(self, catalog: str, schema: str) -> List[str]:
        """List all tables in a schema."""
        catalog_name = catalog or self.config.catalog
        schema_name = schema or self.config.schema

        if not catalog_name or not schema_name:
            raise ValueError("Both catalog and schema must be specified")

        result = self.execute_query(f"SHOW TABLES FROM {catalog_name}.{schema_name}")
        data = json.loads(result)
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

        result = self.execute_query(
            f"SHOW CREATE TABLE {catalog_name}.{schema_name}.{table}"
        )
        data = json.loads(result)
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
