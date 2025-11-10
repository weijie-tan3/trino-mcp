#!/usr/bin/env python3
"""Example usage of the Trino MCP client."""

import os
from trino_mcp.config import load_config
from trino_mcp.client import TrinoClient

# Example 1: List catalogs
print("=" * 60)
print("Example 1: Listing all catalogs")
print("=" * 60)

config = load_config()
client = TrinoClient(config)

try:
    catalogs = client.list_catalogs()
    print(f"Available catalogs: {catalogs}")
except Exception as e:
    print(f"Error: {e}")

# Example 2: Execute a query
print("\n" + "=" * 60)
print("Example 2: Executing a query")
print("=" * 60)

try:
    result = client.execute_query("SELECT 1 as test_column")
    print(f"Query result:\n{result}")
except Exception as e:
    print(f"Error: {e}")

# Example 3: List schemas (if catalog is configured)
if config.catalog:
    print("\n" + "=" * 60)
    print(f"Example 3: Listing schemas in catalog '{config.catalog}'")
    print("=" * 60)

    try:
        schemas = client.list_schemas(config.catalog)
        print(f"Schemas: {schemas}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
