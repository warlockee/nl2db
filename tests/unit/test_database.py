#!/usr/bin/env python3
"""
Integration tests for RedshiftCLI
These tests connect to a real Redshift instance and perform actual operations.
"""
import unittest
import os
from redshift_nl_agent.database import RedshiftCLI


class TestRedshiftCLIIntegration(unittest.TestCase):
    """Integration tests for RedshiftCLI class"""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection once for all tests"""
        cls.HOST = "daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com"
        cls.PORT = 5439
        cls.DATABASE = "prod"
        cls.USER = "moonshoot_dev"
        cls.PASSWORD = os.getenv("REDSHIFT_PASSWORD")

    def setUp(self):
        """Create a new CLI instance before each test"""
        self.cli = RedshiftCLI(
            self.HOST,
            self.PORT,
            self.DATABASE,
            self.USER,
            self.PASSWORD
        )

    def tearDown(self):
        """Clean up after each test"""
        self.cli.close()

    def test_connection_establishment(self):
        """Test that connection to Redshift is established successfully"""
        self.assertIsNotNone(self.cli.conn)
        self.assertIsNotNone(self.cli.cursor)
        self.assertFalse(self.cli.conn.closed)

    def test_select_query_execution(self):
        """Test executing a SELECT query and fetching results"""
        result = self.cli.execute("SELECT 1 AS test_column")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 1)

    def test_select_query_with_multiple_rows(self):
        """Test SELECT query returning multiple rows"""
        sql = """
        SELECT num FROM (
            SELECT 1 AS num
            UNION ALL SELECT 2
            UNION ALL SELECT 3
        ) AS temp
        """
        result = self.cli.execute(sql)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_create_table_and_cleanup(self):
        """Test creating and dropping a temporary table"""
        # Create table
        create_result = self.cli.execute(
            "CREATE TEMP TABLE test_table (id INT, name VARCHAR(50))"
        )
        self.assertEqual(create_result, "Success")

        # Verify table exists
        check_result = self.cli.execute(
            "SELECT COUNT(*) FROM test_table"
        )
        self.assertIsInstance(check_result, list)

        # Drop table
        drop_result = self.cli.execute("DROP TABLE test_table")
        self.assertEqual(drop_result, "Success")

    def test_insert_and_select_data(self):
        """Test inserting data and retrieving it"""
        # Create temp table
        self.cli.execute(
            "CREATE TEMP TABLE test_insert (id INT, value VARCHAR(50))"
        )

        # Insert data
        insert_result = self.cli.execute(
            "INSERT INTO test_insert VALUES (1, 'test_value')"
        )
        self.assertEqual(insert_result, "Success")

        # Select data
        select_result = self.cli.execute(
            "SELECT id, value FROM test_insert WHERE id = 1"
        )
        self.assertEqual(len(select_result), 1)
        self.assertEqual(select_result[0][0], 1)
        self.assertEqual(select_result[0][1], 'test_value')

        # Cleanup
        self.cli.execute("DROP TABLE test_insert")

    def test_update_operation(self):
        """Test UPDATE operation"""
        # Setup
        self.cli.execute(
            "CREATE TEMP TABLE test_update (id INT, status VARCHAR(20))"
        )
        self.cli.execute(
            "INSERT INTO test_update VALUES (1, 'pending')"
        )

        # Update
        update_result = self.cli.execute(
            "UPDATE test_update SET status = 'completed' WHERE id = 1"
        )
        self.assertEqual(update_result, "Success")

        # Verify
        result = self.cli.execute(
            "SELECT status FROM test_update WHERE id = 1"
        )
        self.assertEqual(result[0][0], 'completed')

        # Cleanup
        self.cli.execute("DROP TABLE test_update")

    def test_delete_operation(self):
        """Test DELETE operation"""
        # Setup
        self.cli.execute(
            "CREATE TEMP TABLE test_delete (id INT, name VARCHAR(50))"
        )
        self.cli.execute("INSERT INTO test_delete VALUES (1, 'to_delete')")
        self.cli.execute("INSERT INTO test_delete VALUES (2, 'to_keep')")

        # Delete
        delete_result = self.cli.execute(
            "DELETE FROM test_delete WHERE id = 1"
        )
        self.assertEqual(delete_result, "Success")

        # Verify only one row remains
        result = self.cli.execute("SELECT COUNT(*) FROM test_delete")
        self.assertEqual(result[0][0], 1)

        # Cleanup
        self.cli.execute("DROP TABLE test_delete")

    def test_error_handling_invalid_sql(self):
        """Test error handling with invalid SQL"""
        result = self.cli.execute("INVALID SQL STATEMENT")
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error:"))

    def test_error_handling_nonexistent_table(self):
        """Test error handling when querying non-existent table"""
        result = self.cli.execute(
            "SELECT * FROM nonexistent_table_xyz123"
        )
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error:"))

    def test_connection_close(self):
        """Test that connection closes properly"""
        # Create a separate instance to close
        test_cli = RedshiftCLI(
            self.HOST,
            self.PORT,
            self.DATABASE,
            self.USER,
            self.PASSWORD
        )

        # Verify connection is open
        self.assertFalse(test_cli.conn.closed)

        # Close connection
        test_cli.close()

        # Verify connection is closed
        self.assertTrue(test_cli.conn.closed)

    def test_select_query_case_insensitive(self):
        """Test that SELECT detection is case-insensitive"""
        # Test lowercase
        result = self.cli.execute("select 42")
        self.assertIsInstance(result, list)

        # Test mixed case
        result = self.cli.execute("SeLeCt 99")
        self.assertIsInstance(result, list)

        # Test uppercase
        result = self.cli.execute("SELECT 123")
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
