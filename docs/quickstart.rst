Quick Start
===========

Get up and running with Trino MCP Server in minutes!

Prerequisites
-------------

* Python 3.10 or higher
* A running Trino server
* Trino connection credentials

Step 1: Install
---------------

.. code-block:: bash

   # Using uvx (Recommended)
   uvx trino-mcp

   # Or using uv
   uv pip install trino-mcp
   trino-mcp

   # Or using pip
   pip install trino-mcp
   trino-mcp

Step 2: Configure
-----------------

Create a ``.env`` file in your working directory:

.. code-block:: bash

   TRINO_HOST=localhost
   TRINO_PORT=8080
   TRINO_USER=trino
   TRINO_HTTP_SCHEME=http

For production with authentication:

.. code-block:: bash

   TRINO_HOST=trino.example.com
   TRINO_PORT=8443
   TRINO_USER=your_username
   TRINO_PASSWORD=your_password
   TRINO_HTTP_SCHEME=https
   AUTH_METHOD=PASSWORD

Step 3: Run
-----------

Start the MCP server:

.. code-block:: bash

   trino-mcp

You should see output like:

.. code-block:: text

   2024-01-15 10:00:00 - trino_mcp.server - INFO - Loading Trino configuration...
   2024-01-15 10:00:00 - trino_mcp.server - INFO - Connected to Trino at localhost:8080

Step 4: Connect from MCP Client
--------------------------------

Using Claude Desktop
~~~~~~~~~~~~~~~~~~~~

Edit your Claude Desktop configuration:

.. code-block:: json

   {
     "mcpServers": {
       "trino": {
         "command": "uvx",
         "args": ["trino-mcp"],
         "env": {
           "TRINO_HOST": "localhost",
           "TRINO_PORT": "8080",
           "TRINO_USER": "trino"
         }
       }
     }
   }

Restart Claude Desktop. You should now see "Trino MCP Server" in your available tools!

Step 5: Try It Out
-------------------

Once connected through an MCP client, try these queries:

List Catalogs
~~~~~~~~~~~~~

.. code-block:: text

   What catalogs are available in Trino?

The server will use the ``list_catalogs`` tool to show all available catalogs.

Explore a Schema
~~~~~~~~~~~~~~~~

.. code-block:: text

   Show me the schemas in the hive catalog

The server will use the ``list_schemas`` tool with the hive catalog.

Query a Table
~~~~~~~~~~~~~

.. code-block:: text

   What are the columns in the customers table in hive.default?

The server will use the ``describe_table`` tool to show the table structure.

Execute SQL
~~~~~~~~~~~

.. code-block:: text

   Show me the first 10 rows from hive.default.customers

The server will execute the query using the ``execute_query`` tool.
