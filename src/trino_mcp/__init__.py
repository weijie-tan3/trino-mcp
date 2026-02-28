"""Trino MCP Server - A simple Model Context Protocol server for Trino."""

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"  # fallback for editable installs without build

# Export main classes for library usage
from .client import TrinoClient
from .config import TrinoConfig, load_config

__all__ = ["TrinoClient", "TrinoConfig", "load_config", "__version__"]
