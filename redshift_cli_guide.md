# Redshift CLI User Guide

## Overview
RedshiftCLI is a Python-based command-line interface for interacting with AWS Redshift databases using psycopg2.

## Class: RedshiftCLI

### Constructor
```python
RedshiftCLI(host, port, database, user, password)
```

**Parameters:**
- `host` (str): Redshift endpoint hostname
- `port` (int): Connection port (typically 5439)
- `database` (str): Database name
- `user` (str): Database username
- `password` (str): Database password

**Returns:** RedshiftCLI instance with active database connection

### Methods

#### execute(sql)
Executes SQL statements and returns appropriate results.

**Parameters:**
- `sql` (str): SQL query or command to execute

**Returns:**
- For SELECT queries: List of tuples containing query results
- For non-SELECT queries: String "Success" on successful execution
- On error: String starting with "Error: " followed by error message

**Behavior:**
- SELECT queries (case-insensitive): Fetches and returns all rows
- Non-SELECT queries (INSERT, UPDATE, DELETE, CREATE, etc.): Commits transaction and returns success message
- Exceptions are caught and returned as error strings

#### close()
Closes the database cursor and connection.

**Parameters:** None

**Returns:** None

## Usage Examples

### Basic Connection and Query
```python
from redshift_cli import RedshiftCLI

cli = RedshiftCLI(
    host="your-cluster.region.redshift.amazonaws.com",
    port=5439,
    database="prod",
    user="username",
    password="password"
)

# Execute SELECT query
result = cli.execute("SELECT * FROM users LIMIT 10")
print(result)  # [(row1_data,), (row2_data,), ...]

# Close connection
cli.close()
```

### Creating Tables
```python
cli = RedshiftCLI(host, port, database, user, password)

result = cli.execute("""
    CREATE TABLE products (
        id INT PRIMARY KEY,
        name VARCHAR(100),
        price DECIMAL(10,2)
    )
""")
print(result)  # "Success"

cli.close()
```

### Inserting Data
```python
cli = RedshiftCLI(host, port, database, user, password)

result = cli.execute(
    "INSERT INTO products VALUES (1, 'Widget', 29.99)"
)
print(result)  # "Success"

cli.close()
```

### Updating Records
```python
cli = RedshiftCLI(host, port, database, user, password)

result = cli.execute(
    "UPDATE products SET price = 24.99 WHERE id = 1"
)
print(result)  # "Success"

cli.close()
```

### Deleting Records
```python
cli = RedshiftCLI(host, port, database, user, password)

result = cli.execute("DELETE FROM products WHERE id = 1")
print(result)  # "Success"

cli.close()
```

### Error Handling
```python
cli = RedshiftCLI(host, port, database, user, password)

result = cli.execute("INVALID SQL")
print(result)  # "Error: syntax error at or near ..."

cli.close()
```

## Interactive CLI Mode

The script includes an interactive mode when run directly:

```bash
python3 redshift_cli.py
```

**Interactive Commands:**
- Enter SQL statements at the `redshift>` prompt
- Type `quit` to exit
- Results are displayed immediately after each query

**Example Session:**
```
Redshift CLI - 输入 'quit' 退出
redshift> SELECT COUNT(*) FROM users
[(42,)]
redshift> SELECT current_database()
[('prod',)]
redshift> quit
```

## Important Notes

1. **Connection Management**: Always call `close()` when done to free resources
2. **Query Detection**: SELECT queries are detected case-insensitively by checking if SQL starts with "SELECT"
3. **Transaction Handling**: Non-SELECT queries automatically commit; no manual commit needed
4. **Error Format**: Errors are returned as strings, not raised as exceptions
5. **Result Format**: SELECT results are lists of tuples, where each tuple represents a row

## Dependencies

```python
pip install psycopg2-binary
```

## Common Query Patterns

### Count Records
```python
result = cli.execute("SELECT COUNT(*) FROM table_name")
count = result[0][0]
```

### Check Table Exists
```python
result = cli.execute("""
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_name = 'your_table'
""")
exists = result[0][0] > 0
```

### Get Current Database
```python
result = cli.execute("SELECT current_database()")
db_name = result[0][0]
```

### List Tables
```python
result = cli.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
""")
tables = [row[0] for row in result]
```
