#!/usr/bin/env python3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

class RedshiftCLI:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """Establish database connection with autocommit to prevent transaction cascade failures"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass

        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        # Set autocommit mode to prevent transaction cascade failures
        # Each query is auto-committed, so errors don't poison the connection
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()

    def execute(self, sql):
        try:
            # Ensure connection is open
            if self.conn.closed:
                self._connect()

            self.cursor.execute(sql)
            if sql.strip().upper().startswith('SELECT') or sql.strip().upper().startswith('WITH'):
                return self.cursor.fetchall()
            else:
                # In autocommit mode, no need to commit manually
                return "Success"
        except Exception as e:
            # In autocommit mode, each statement is isolated
            # No transaction cascade, but we return the error
            return f"Error: {e}"
    
    def close(self):
        self.cursor.close()
        self.conn.close()

# Usage example
if __name__ == "__main__":
    import os

    # Get connection details from environment variables
    HOST = os.getenv('REDSHIFT_HOST', 'daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com')
    PORT = int(os.getenv('REDSHIFT_PORT', '5439'))
    DATABASE = os.getenv('REDSHIFT_DATABASE', 'prod')
    USER = os.getenv('REDSHIFT_USER')
    PASSWORD = os.getenv('REDSHIFT_PASSWORD')

    if not USER or not PASSWORD:
        print("Error: Please set REDSHIFT_USER and REDSHIFT_PASSWORD environment variables")
        print("Example: export REDSHIFT_USER=your_user REDSHIFT_PASSWORD=your_password")
        sys.exit(1)

    cli = RedshiftCLI(HOST, PORT, DATABASE, USER, PASSWORD)

    # Interactive command line
    print("Redshift CLI - Type 'quit' to exit")
    while True:
        sql = input("redshift> ")
        if sql.lower() == 'quit':
            break
        result = cli.execute(sql)
        print(result)

    cli.close()
