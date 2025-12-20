Available Tools
===============

Trino MCP Server provides several tools for interacting with your Trino cluster. Each tool is exposed through the Model Context Protocol and can be called by MCP clients.

list_catalogs
-------------

List all available catalogs in the Trino cluster.

**Parameters:** None

**Returns:** A list of catalog names, one per line

**Example Usage:**

.. code-block:: text

   What catalogs are available?

**Example Response:**

.. code-block:: text

   system
   hive
   mysql
   postgresql

list_schemas
------------

List all schemas in a specific catalog.

**Parameters:**

* ``catalog`` (string, required): The name of the catalog

**Returns:** A list of schema names, one per line

**Example Usage:**

.. code-block:: text

   Show me the schemas in the hive catalog

**Example Response:**

.. code-block:: text

   default
   production
   staging
   analytics

list_tables
-----------

List all tables in a specific schema.

**Parameters:**

* ``catalog`` (string, required): The name of the catalog
* ``schema`` (string, required): The name of the schema

**Returns:** A list of table names, one per line

**Example Usage:**

.. code-block:: text

   List all tables in hive.production

**Example Response:**

.. code-block:: text

   customers
   orders
   products
   inventory

describe_table
--------------

Describe the structure of a table, including columns, data types, and comments.

**Parameters:**

* ``table`` (string, required): The name of the table
* ``catalog`` (string, optional): The name of the catalog
* ``schema`` (string, optional): The name of the schema

**Returns:** Table structure in formatted text

execute_query
-------------

Execute a SQL query and return results in JSON format.

**Parameters:**

* ``query`` (string, required): The SQL query to execute

**Returns:** Query results as JSON

.. warning::
   Be cautious when executing queries without LIMIT clauses. Large result sets may take time to process and return.

show_create_table
-----------------

Show the CREATE TABLE statement for a table.

**Parameters:**

* ``table`` (string, required): The name of the table
* ``catalog`` (string, optional): The name of the catalog
* ``schema`` (string, optional): The name of the schema

**Returns:** The CREATE TABLE SQL statement

get_table_stats
---------------

Get statistics for a table, such as row count and size.

**Parameters:**

* ``table`` (string, required): The name of the table
* ``catalog`` (string, optional): The name of the catalog
* ``schema`` (string, optional): The name of the schema

**Returns:** Table statistics as formatted text
