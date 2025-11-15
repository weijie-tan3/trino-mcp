# Available Tools

Trino MCP Server provides several tools for interacting with your Trino cluster. Each tool is exposed through the Model Context Protocol and can be called by MCP clients.

## list_catalogs

List all available catalogs in the Trino cluster.

**Parameters:** None

**Returns:** A list of catalog names, one per line

**Example Usage:**
```
What catalogs are available?
```

**Example Response:**
```
system
hive
mysql
postgresql
```

---

## list_schemas

List all schemas in a specific catalog.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `catalog` | string | Yes | The name of the catalog |

**Returns:** A list of schema names, one per line

**Example Usage:**
```
Show me the schemas in the hive catalog
```

**Example Response:**
```
default
production
staging
analytics
```

---

## list_tables

List all tables in a specific schema.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `catalog` | string | Yes | The name of the catalog |
| `schema` | string | Yes | The name of the schema |

**Returns:** A list of table names, one per line

**Example Usage:**
```
List all tables in hive.production
```

**Example Response:**
```
customers
orders
products
inventory
```

---

## describe_table

Describe the structure of a table, including columns, data types, and comments.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `table` | string | Yes | The name of the table |
| `catalog` | string | No* | The name of the catalog |
| `schema` | string | No* | The name of the schema |

*If `catalog` and `schema` are not provided, defaults from configuration will be used if available.

**Returns:** Table structure in formatted text

**Example Usage:**
```
Describe the structure of hive.production.customers
```

**Example Response:**
```
Table: hive.production.customers

Columns:
- customer_id (bigint): Unique customer identifier
- name (varchar): Customer full name
- email (varchar): Customer email address
- created_at (timestamp): Account creation timestamp
- country (varchar): Customer country code
```

---

## execute_query

Execute a SQL query and return results in JSON format.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | The SQL query to execute |

**Returns:** Query results as JSON

**Example Usage:**
```
Execute: SELECT country, COUNT(*) as count FROM hive.production.customers GROUP BY country LIMIT 5
```

**Example Response:**
```json
[
  {"country": "US", "count": 15234},
  {"country": "UK", "count": 8901},
  {"country": "CA", "count": 5678},
  {"country": "DE", "count": 4321},
  {"country": "FR", "count": 3456}
]
```

!!! warning "Query Limits"
    Be cautious when executing queries without LIMIT clauses. Large result sets may take time to process and return.

---

## show_create_table

Show the CREATE TABLE statement for a table.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `table` | string | Yes | The name of the table |
| `catalog` | string | No* | The name of the catalog |
| `schema` | string | No* | The name of the schema |

*If `catalog` and `schema` are not provided, defaults from configuration will be used if available.

**Returns:** The CREATE TABLE SQL statement

**Example Usage:**
```
Show me the CREATE TABLE statement for hive.production.customers
```

**Example Response:**
```sql
CREATE TABLE hive.production.customers (
   customer_id bigint,
   name varchar,
   email varchar,
   created_at timestamp,
   country varchar
)
WITH (
   format = 'PARQUET',
   partitioned_by = ARRAY['country']
)
```

---

## get_table_stats

Get statistics for a table, such as row count and size.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `table` | string | Yes | The name of the table |
| `catalog` | string | No* | The name of the catalog |
| `schema` | string | No* | The name of the schema |

*If `catalog` and `schema` are not provided, defaults from configuration will be used if available.

**Returns:** Table statistics as formatted text

**Example Usage:**
```
What are the statistics for hive.production.customers?
```

**Example Response:**
```
Table Statistics: hive.production.customers

Row Count: 1,234,567
Data Size: 2.5 GB
Partitions: 50
Last Modified: 2024-01-15 10:30:00
```

---

## Tool Usage Best Practices

### 1. Progressive Discovery

Start broad and narrow down:

```
1. What catalogs are available?
2. Show me schemas in the hive catalog
3. List tables in hive.production
4. Describe hive.production.customers
5. Query the customers table
```

### 2. Fully Qualify Table Names

Always use fully qualified table names when possible:

✅ Good: `hive.production.customers`
❌ Avoid: `customers` (unless defaults are configured)

### 3. Limit Large Queries

Always use LIMIT for exploratory queries:

✅ Good: `SELECT * FROM large_table LIMIT 10`
❌ Avoid: `SELECT * FROM large_table`

### 4. Handle Errors Gracefully

If a query fails:
1. Check the error message
2. Verify table/schema/catalog names
3. Ensure you have proper permissions
4. Try a simpler query first

### 5. Use Appropriate Tools

- Use `describe_table` instead of `SELECT * LIMIT 1` to understand structure
- Use `get_table_stats` instead of `COUNT(*)` for quick size estimates
- Use `show_create_table` to understand partitioning and storage format

## Error Handling

All tools return error messages if something goes wrong:

```
Error listing catalogs: Connection refused
Error executing query: Permission denied for table hive.production.customers
Error describing table: Table hive.production.nonexistent does not exist
```

## Next Steps

- [Examples](examples.md) - See complete usage examples
- [Authentication](authentication.md) - Configure authentication
- [API Reference](api.md) - Detailed API documentation
