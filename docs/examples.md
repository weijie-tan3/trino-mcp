# Examples

This page provides practical examples of using Trino MCP Server with MCP clients.

## Basic Operations

### List Available Catalogs

**User Query:**
```
What Trino catalogs are available?
```

**MCP Tool Call:**
```python
list_catalogs()
```

**Response:**
```
system
hive
mysql
postgresql
mongodb
```

---

### Explore a Catalog

**User Query:**
```
Show me all schemas in the hive catalog
```

**MCP Tool Call:**
```python
list_schemas(catalog="hive")
```

**Response:**
```
default
production
staging
analytics
raw_data
```

---

### List Tables in a Schema

**User Query:**
```
What tables are in the production schema of the hive catalog?
```

**MCP Tool Call:**
```python
list_tables(catalog="hive", schema="production")
```

**Response:**
```
customers
orders
products
inventory
transactions
```

---

## Table Inspection

### Describe Table Structure

**User Query:**
```
What columns does the customers table have in hive.production?
```

**MCP Tool Call:**
```python
describe_table(table="customers", catalog="hive", schema="production")
```

**Response:**
```
Table: hive.production.customers

Columns:
- customer_id (bigint): Unique customer identifier
- first_name (varchar): Customer first name
- last_name (varchar): Customer last name
- email (varchar): Customer email address
- phone (varchar): Customer phone number
- address (varchar): Customer address
- city (varchar): Customer city
- state (varchar): Customer state
- country (varchar): Customer country
- created_at (timestamp): Account creation timestamp
- updated_at (timestamp): Last update timestamp
```

---

### Show CREATE TABLE Statement

**User Query:**
```
Show me how the orders table is defined
```

**MCP Tool Call:**
```python
show_create_table(table="orders", catalog="hive", schema="production")
```

**Response:**
```sql
CREATE TABLE hive.production.orders (
   order_id bigint,
   customer_id bigint,
   order_date date,
   total_amount decimal(10,2),
   status varchar,
   created_at timestamp
)
WITH (
   format = 'PARQUET',
   partitioned_by = ARRAY['order_date']
)
```

---

### Get Table Statistics

**User Query:**
```
What are the statistics for the orders table?
```

**MCP Tool Call:**
```python
get_table_stats(table="orders", catalog="hive", schema="production")
```

**Response:**
```
Table Statistics: hive.production.orders

Row Count: 5,234,567
Data Size: 12.3 GB
Partitions: 365
Last Modified: 2024-01-15 08:30:00
```

---

## Data Querying

### Simple SELECT Query

**User Query:**
```
Show me 5 customers from the database
```

**MCP Tool Call:**
```python
execute_query(query="SELECT * FROM hive.production.customers LIMIT 5")
```

**Response:**
```json
[
  {
    "customer_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "country": "US",
    "created_at": "2023-01-15T10:30:00"
  },
  {
    "customer_id": 2,
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "country": "UK",
    "created_at": "2023-02-20T14:45:00"
  },
  ...
]
```

---

### Aggregation Query

**User Query:**
```
How many orders do we have by status?
```

**MCP Tool Call:**
```python
execute_query(query="""
    SELECT status, COUNT(*) as order_count
    FROM hive.production.orders
    GROUP BY status
    ORDER BY order_count DESC
""")
```

**Response:**
```json
[
  {"status": "completed", "order_count": 4567890},
  {"status": "pending", "order_count": 345678},
  {"status": "cancelled", "order_count": 123456},
  {"status": "processing", "order_count": 98765}
]
```

---

### JOIN Query

**User Query:**
```
Show me recent orders with customer information
```

**MCP Tool Call:**
```python
execute_query(query="""
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
""")
```

**Response:**
```json
[
  {
    "order_id": 12345,
    "order_date": "2024-01-15",
    "total_amount": 299.99,
    "first_name": "Alice",
    "last_name": "Johnson",
    "email": "alice.j@example.com"
  },
  ...
]
```

---

## Real-World Scenarios

### Scenario 1: Data Discovery

**Goal:** Find and understand available customer data

**Conversation Flow:**

1. **User:** "What data sources do we have?"
   - Tool: `list_catalogs()`
   - Response: Lists all catalogs

2. **User:** "Show me what's in the hive catalog"
   - Tool: `list_schemas(catalog="hive")`
   - Response: Lists schemas

3. **User:** "What tables are in the production schema?"
   - Tool: `list_tables(catalog="hive", schema="production")`
   - Response: Lists tables including "customers"

4. **User:** "Describe the customers table"
   - Tool: `describe_table(table="customers", catalog="hive", schema="production")`
   - Response: Shows all columns and types

---

### Scenario 2: Data Analysis

**Goal:** Analyze customer distribution by country

**Conversation Flow:**

1. **User:** "How many customers do we have by country?"
   ```python
   execute_query(query="""
       SELECT country, COUNT(*) as customer_count
       FROM hive.production.customers
       GROUP BY country
       ORDER BY customer_count DESC
       LIMIT 10
   """)
   ```

2. **User:** "What percentage is that of total customers?"
   ```python
   execute_query(query="""
       SELECT 
           country,
           COUNT(*) as customer_count,
           ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
       FROM hive.production.customers
       GROUP BY country
       ORDER BY customer_count DESC
       LIMIT 10
   """)
   ```

---

### Scenario 3: Troubleshooting

**Goal:** Investigate data quality issues

**Conversation Flow:**

1. **User:** "Check for customers with missing email addresses"
   ```python
   execute_query(query="""
       SELECT COUNT(*) as missing_emails
       FROM hive.production.customers
       WHERE email IS NULL OR email = ''
   """)
   ```

2. **User:** "Show me examples of those customers"
   ```python
   execute_query(query="""
       SELECT customer_id, first_name, last_name, created_at
       FROM hive.production.customers
       WHERE email IS NULL OR email = ''
       LIMIT 10
   """)
   ```

---

### Scenario 4: Performance Analysis

**Goal:** Understand table sizes and optimize queries

**Conversation Flow:**

1. **User:** "What are the largest tables in production?"
   ```python
   # Get stats for each table
   get_table_stats(table="customers", catalog="hive", schema="production")
   get_table_stats(table="orders", catalog="hive", schema="production")
   get_table_stats(table="products", catalog="hive", schema="production")
   ```

2. **User:** "How is the orders table partitioned?"
   ```python
   show_create_table(table="orders", catalog="hive", schema="production")
   ```

---

## Advanced Patterns

### Pattern 1: Progressive Refinement

Start broad, then narrow down:

```
1. "What catalogs exist?" → All catalogs
2. "Show schemas in hive" → All schemas
3. "List tables in production" → All tables
4. "Describe customers table" → Table structure
5. "Show 10 sample rows" → Actual data
```

### Pattern 2: Cross-Catalog Queries

Query across multiple catalogs:

```python
execute_query(query="""
    SELECT 
        h.customer_id,
        h.name,
        m.last_login,
        p.total_purchases
    FROM hive.production.customers h
    LEFT JOIN mysql.app.user_sessions m ON h.customer_id = m.user_id
    LEFT JOIN postgresql.analytics.purchase_summary p ON h.customer_id = p.customer_id
    WHERE h.created_at >= DATE '2024-01-01'
    LIMIT 100
""")
```

### Pattern 3: Complex Analytics

Multi-step analysis:

```python
# Step 1: Get date range
execute_query(query="""
    SELECT 
        MIN(order_date) as first_order,
        MAX(order_date) as last_order
    FROM hive.production.orders
""")

# Step 2: Analyze trends
execute_query(query="""
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        COUNT(*) as order_count,
        SUM(total_amount) as revenue
    FROM hive.production.orders
    WHERE order_date >= DATE '2023-01-01'
    GROUP BY DATE_TRUNC('month', order_date)
    ORDER BY month
""")
```

---

## Tips and Tricks

### Use LIMIT for Exploration

Always use LIMIT when exploring data:

```sql
✅ SELECT * FROM large_table LIMIT 10
❌ SELECT * FROM large_table
```

### Fully Qualify Table Names

Be explicit about catalog and schema:

```sql
✅ SELECT * FROM hive.production.customers
❌ SELECT * FROM customers
```

### Check Table Stats First

Before querying, check table size:

```python
get_table_stats(table="huge_table", catalog="hive", schema="production")
```

### Use EXPLAIN for Complex Queries

Understand query execution:

```python
execute_query(query="EXPLAIN SELECT * FROM hive.production.orders WHERE order_date = DATE '2024-01-15'")
```

---

## Next Steps

- [Available Tools](tools.md) - Complete tool reference
- [API Reference](api.md) - Detailed API documentation
- [Configuration](configuration.md) - Advanced configuration
