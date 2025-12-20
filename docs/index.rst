Trino MCP Server
================

A simple and powerful Model Context Protocol (MCP) server for the Trino query engine with OAuth support.

Overview
--------

Trino MCP Server provides a seamless interface between Large Language Models and Trino query engine through the Model Context Protocol. It enables AI assistants to interact with your Trino cluster, query data, and explore database schemas naturally.

Key Features
------------

* 🔍 **Core Trino Operations**: Query catalogs, schemas, tables, and execute SQL queries
* 🔐 **OAuth Support**: Built-in OAuth2 authentication without requiring explicit JWT tokens
* 🔒 **Basic Authentication**: Also supports username/password authentication
* ⚡ **Simple & Focused**: Core Trino features without over-complication
* 📦 **uvx Compatible**: Run directly with ``uvx`` without installation
* 🐍 **Python 3.10+**: Modern Python support

Quick Start
-----------

.. code-block:: bash

   # Install and run with uvx
   uvx trino-mcp

   # Or install with uv/pip
   uv pip install trino-mcp
   trino-mcp

Prerequisites
-------------

* Python 3.10 or higher
* A running Trino server
* (Optional) Trino credentials for authentication

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   configuration
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: Usage

   tools
   authentication
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
