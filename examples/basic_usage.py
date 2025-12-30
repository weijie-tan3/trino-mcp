#!/usr/bin/env python3
"""Example usage of the Trino MCP client."""

import os
import sys

# Add the src directory to the path for local development
# This allows running the example without installing the package
_src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if os.path.exists(_src_path):
    sys.path.insert(0, _src_path)

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

# Example 2: Execute a query with execute_query (returns JSON string)
print("\n" + "=" * 60)
print("Example 2: Executing a query with execute_query (JSON string)")
print("=" * 60)

try:
    result = client.execute_query("SELECT 1 as test_column")
    print(f"Query result (JSON string):\n{result}")
    print(f"Type: {type(result)}")
except Exception as e:
    print(f"Error: {e}")

# Example 3: Execute a query with execute_query_raw (returns Python data structures)
print("\n" + "=" * 60)
print("Example 3: Executing a query with execute_query_raw (native Python)")
print("=" * 60)

try:
    result = client.execute_query_raw("SELECT 1 as test_column, 2 as another_column")
    print(f"Query result (Python list):\n{result}")
    print(f"Type: {type(result)}")
    print(f"First row: {result[0]}")
    print(f"Accessing column: test_column = {result[0]['test_column']}")
except Exception as e:
    print(f"Error: {e}")

# Example 4: List schemas (if catalog is configured)
if config.catalog:
    print("\n" + "=" * 60)
    print(f"Example 4: Listing schemas in catalog '{config.catalog}'")
    print("=" * 60)

    try:
        schemas = client.list_schemas(config.catalog)
        print(f"Schemas: {schemas}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
print("\nNote: Use execute_query_raw() for library usage to get native Python data structures.")
print("      Use execute_query() when you need JSON strings (e.g., for MCP server).")
