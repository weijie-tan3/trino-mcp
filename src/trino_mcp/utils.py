"""Trino MCP Server - Utility functions."""

import logging

import sqlglot
from sqlglot.expressions import (
    Alter,
    Analyze,
    Command,
    Create,
    Delete,
    Describe,
    Drop,
    Grant,
    Insert,
    Merge,
    Refresh,
    Revoke,
    TruncateTable,
    Update,
)

logger = logging.getLogger(__name__)

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


def is_read_only_query(query: str) -> bool:
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
