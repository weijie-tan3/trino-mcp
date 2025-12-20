Examples
========

This page provides practical examples of using Trino MCP Server with MCP clients.

Basic Operations
----------------

List Available Catalogs
~~~~~~~~~~~~~~~~~~~~~~~

**User Query:**

.. code-block:: text

   What Trino catalogs are available?

**Response:**

.. code-block:: text

   system
   hive
   mysql
   postgresql
   mongodb

Explore a Catalog
~~~~~~~~~~~~~~~~~

**User Query:**

.. code-block:: text

   Show me all schemas in the hive catalog

**Response:**

.. code-block:: text

   default
   production
   staging
   analytics
   raw_data

Data Querying
-------------

Simple SELECT Query
~~~~~~~~~~~~~~~~~~~

**User Query:**

.. code-block:: text

   Show me 5 customers from the database

**SQL Executed:**

.. code-block:: sql

   SELECT * FROM hive.production.customers LIMIT 5

Aggregation Query
~~~~~~~~~~~~~~~~~

**User Query:**

.. code-block:: text

   How many orders do we have by status?

**SQL Executed:**

.. code-block:: sql

   SELECT status, COUNT(*) as order_count
   FROM hive.production.orders
   GROUP BY status
   ORDER BY order_count DESC

JOIN Query
~~~~~~~~~~

**User Query:**

.. code-block:: text

   Show me recent orders with customer information

**SQL Executed:**

.. code-block:: sql

   SELECT 
       o.order_id,
       o.order_date,
       o.total_amount,
       c.first_name,
       c.last_name,
       c.email
   FROM hive.production.orders o
   JOIN hive.production.customers c ON o.customer_id = c.customer_id
   WHERE o.order_date >= DATE '2024-01-01'
   ORDER BY o.order_date DESC
   LIMIT 10

Real-World Scenarios
--------------------

Scenario 1: Data Discovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Goal:** Find and understand available customer data

**Conversation Flow:**

1. "What data sources do we have?" → Lists all catalogs
2. "Show me what's in the hive catalog" → Lists schemas
3. "What tables are in the production schema?" → Lists tables
4. "Describe the customers table" → Shows table structure

Scenario 2: Data Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Goal:** Analyze customer distribution by country

**Queries:**

1. Count customers by country:

   .. code-block:: sql

      SELECT country, COUNT(*) as customer_count
      FROM hive.production.customers
      GROUP BY country
      ORDER BY customer_count DESC
      LIMIT 10

2. Calculate percentages:

   .. code-block:: sql

      SELECT 
          country,
          COUNT(*) as customer_count,
          ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
      FROM hive.production.customers
      GROUP BY country
      ORDER BY customer_count DESC
      LIMIT 10

Best Practices
--------------

Use LIMIT for Exploration
~~~~~~~~~~~~~~~~~~~~~~~~~

Always use LIMIT when exploring data:

.. code-block:: sql

   -- Good
   SELECT * FROM large_table LIMIT 10
   
   -- Avoid
   SELECT * FROM large_table

Fully Qualify Table Names
~~~~~~~~~~~~~~~~~~~~~~~~~~

Be explicit about catalog and schema:

.. code-block:: sql

   -- Good
   SELECT * FROM hive.production.customers
   
   -- Avoid (unless defaults are configured)
   SELECT * FROM customers
