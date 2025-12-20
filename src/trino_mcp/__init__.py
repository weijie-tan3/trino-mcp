"""Trino MCP Server - A simple Model Context Protocol server for Trino."""

__version__ = "0.1.0"

# Export main classes for library usage
from .client import TrinoClient
from .config import TrinoConfig, load_config

__all__ = ["TrinoClient", "TrinoConfig", "load_config", "__version__"]
