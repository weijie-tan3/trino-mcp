# Trino MCP Server

A simple and powerful Model Context Protocol (MCP) server for the Trino query engine with OAuth support.

## Overview

Trino MCP Server provides a seamless interface between Large Language Models and Trino query engine through the Model Context Protocol. It enables AI assistants to interact with your Trino cluster, query data, and explore database schemas naturally.

## Key Features

- **🔍 Core Trino Operations**: Query catalogs, schemas, tables, and execute SQL queries
- **🔐 OAuth Support**: Built-in OAuth2 authentication without requiring explicit JWT tokens
- **🔒 Basic Authentication**: Also supports username/password authentication
- **⚡ Simple & Focused**: Core Trino features without over-complication
- **📦 uvx Compatible**: Run directly with `uvx` without installation
- **🐍 Python 3.10+**: Modern Python support

## Quick Start

```bash
# Install and run with uvx
uvx trino-mcp

# Or install with uv/pip
uv pip install trino-mcp
trino-mcp
```

## Use Cases

- **Interactive SQL Queries**: Let AI assistants help you query your Trino data warehouse
- **Schema Exploration**: Discover catalogs, schemas, and tables through natural language
- **Data Analysis**: Execute complex SQL queries with AI assistance
- **Database Documentation**: Generate documentation for your Trino tables and schemas

## Prerequisites

- Python 3.10 or higher
- A running Trino server
- (Optional) Trino credentials for authentication

## What is MCP?

The Model Context Protocol (MCP) is an open standard for connecting AI assistants to external data sources and tools. It enables Large Language Models to interact with databases, APIs, and other systems in a standardized way.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│             │   MCP   │              │  Trino  │            │
│  AI Client  │◄───────►│  MCP Server  │◄────────│   Trino    │
│  (Claude)   │         │  (This pkg)  │         │  Cluster   │
└─────────────┘         └──────────────┘         └────────────┘
```

## Next Steps

- [Installation Guide](installation.md) - Get started with installation
- [Configuration](configuration.md) - Configure your Trino connection
- [Available Tools](tools.md) - Explore available MCP tools
- [Examples](examples.md) - See usage examples

## Community

- [GitHub Repository](https://github.com/weijie-tan3/trino-mcp)
- [Issue Tracker](https://github.com/weijie-tan3/trino-mcp/issues)
- [Trino Documentation](https://trino.io/docs/)
- [MCP Documentation](https://modelcontextprotocol.io/)
