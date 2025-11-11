"""Trino client for executing queries."""

import json
from typing import List

import trino
from trino.dbapi import Connection, Cursor

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

    def execute_query(self, query: str) -> str:
        """Execute a SQL query and return results as JSON string."""
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
