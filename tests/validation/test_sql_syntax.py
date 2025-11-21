#!/usr/bin/env python3
"""
Test SQL Syntax Generation - Verify 100% Valid SQL
Tests that all generated SQL has proper clause ordering: SELECT -> FROM -> WHERE -> ORDER BY -> LIMIT
"""
import sys
import os

from redshift_nl_agent.agent import RedshiftAgent
import re


def validate_sql_syntax(sql: str) -> tuple[bool, str]:
    """
    Validate that SQL has proper clause ordering
    Returns: (is_valid, error_message)
    """
    sql_upper = sql.upper().strip()

    # Basic structure check
    if not sql_upper.startswith('SELECT'):
        return False, "SQL must start with SELECT"

    # Find positions of key clauses
    from_pos = sql_upper.find(' FROM ')
    where_pos = sql_upper.find(' WHERE ')
    order_pos = sql_upper.find(' ORDER BY ')
    limit_pos = sql_upper.find(' LIMIT ')

    # Check FROM is present
    if from_pos == -1:
        return False, "SQL must have FROM clause"

    # Check clause ordering
    positions = {}
    if from_pos >= 0:
        positions['FROM'] = from_pos
    if where_pos >= 0:
        positions['WHERE'] = where_pos
    if order_pos >= 0:
        positions['ORDER BY'] = order_pos
    if limit_pos >= 0:
        positions['LIMIT'] = limit_pos

    # Verify proper ordering
    if where_pos >= 0 and limit_pos >= 0:
        if where_pos > limit_pos:
            return False, f"WHERE must come before LIMIT (WHERE at {where_pos}, LIMIT at {limit_pos})"

    if order_pos >= 0 and limit_pos >= 0:
        if order_pos > limit_pos:
            return False, f"ORDER BY must come before LIMIT (ORDER at {order_pos}, LIMIT at {limit_pos})"

    if where_pos >= 0 and order_pos >= 0:
        if where_pos > order_pos:
            return False, f"WHERE must come before ORDER BY (WHERE at {where_pos}, ORDER at {order_pos})"

    # Check for LIMIT after WHERE (common bug)
    if 'LIMIT' in sql_upper and 'WHERE' in sql_upper:
        # Pattern: LIMIT xxx WHERE (this is wrong)
        if re.search(r'LIMIT\s+\d+\s+WHERE', sql_upper):
            return False, "Found 'LIMIT xxx WHERE' pattern - LIMIT must come AFTER WHERE"

    return True, "Valid SQL syntax"


def test_rule_based_sql_generation():
    """Test rule-based SQL generation with various queries"""
    print("\n" + "="*80)
    print("TEST: Rule-Based SQL Generation Syntax")
    print("="*80)

    # Create agent without API keys (forces rule-based mode)
    HOST = "daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com"
    PORT = 5439
    DATABASE = "prod"
    USER = "moonshoot_dev"
    PASSWORD = os.getenv("REDSHIFT_PASSWORD")

    agent = RedshiftAgent(HOST, PORT, DATABASE, USER, PASSWORD)

    # Test queries that previously failed
    test_queries = [
        "show me camera events from the past week",
        "show me events from the last month",
        "get data from today",
        "show me cameras from the past week",
        "count events from the past week",
        "top 10 cameras from the past week",
        "show me all cameras",
        "count all fleets",
        "top 5 most recent cameras",
    ]

    all_passed = True
    results = []

    for query in test_queries:
        print(f"\n📝 Query: {query}")

        # Generate SQL using explain mode (doesn't execute)
        result = agent.query(query, explain=True)
        sql = result['sql']

        print(f"   Generated SQL: {sql}")

        # Validate syntax
        is_valid, error = validate_sql_syntax(sql)

        if is_valid:
            print(f"   ✅ VALID - {error}")
            results.append((query, sql, True, error))
        else:
            print(f"   ❌ INVALID - {error}")
            results.append((query, sql, False, error))
            all_passed = False

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    passed = sum(1 for r in results if r[2])
    total = len(results)

    print(f"\nTests Passed: {passed}/{total} ({100*passed//total}%)")

    if all_passed:
        print("\n✅ ALL TESTS PASSED - 100% Valid SQL Syntax")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nFailed queries:")
        for query, sql, passed, error in results:
            if not passed:
                print(f"  - {query}")
                print(f"    SQL: {sql}")
                print(f"    Error: {error}")

    agent.close()
    return all_passed


def test_specific_bug_case():
    """Test the specific bug case reported by user"""
    print("\n" + "="*80)
    print("TEST: Specific Bug Case - 'show me camera events from the past week'")
    print("="*80)

    HOST = "daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com"
    PORT = 5439
    DATABASE = "prod"
    USER = "moonshoot_dev"
    PASSWORD = os.getenv("REDSHIFT_PASSWORD")

    agent = RedshiftAgent(HOST, PORT, DATABASE, USER, PASSWORD)

    query = "show me camera events from the past week"
    print(f"\n📝 Testing: {query}")

    result = agent.query(query, explain=True)
    sql = result['sql']

    print(f"   Generated SQL: {sql}")

    # Check for the specific bug pattern
    if re.search(r'LIMIT\s+\d+\s+WHERE', sql, re.IGNORECASE):
        print("   ❌ BUG STILL EXISTS: Found 'LIMIT xxx WHERE' pattern")
        print("   This is the exact bug that was reported!")
        agent.close()
        return False

    # Validate full syntax
    is_valid, error = validate_sql_syntax(sql)

    if is_valid:
        print(f"   ✅ BUG FIXED - {error}")
        agent.close()
        return True
    else:
        print(f"   ❌ STILL INVALID - {error}")
        agent.close()
        return False


def test_sql_execution():
    """Test that fixed SQL actually executes without errors"""
    print("\n" + "="*80)
    print("TEST: SQL Execution (Actually Run Queries)")
    print("="*80)

    HOST = "daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com"
    PORT = 5439
    DATABASE = "prod"
    USER = "moonshoot_dev"
    PASSWORD = os.getenv("REDSHIFT_PASSWORD")

    agent = RedshiftAgent(HOST, PORT, DATABASE, USER, PASSWORD)

    test_queries = [
        "show me camera events from the past week",
        "count cameras from the past month",
        "show me fleets from today",
    ]

    all_passed = True

    for query in test_queries:
        print(f"\n📝 Query: {query}")

        result = agent.query(query)

        print(f"   SQL: {result['sql']}")

        if result['error']:
            print(f"   ❌ EXECUTION FAILED: {result['error']}")
            all_passed = False
        else:
            row_count = len(result['results']) if isinstance(result['results'], list) else 0
            print(f"   ✅ EXECUTED SUCCESSFULLY - {row_count} rows returned")
            print(f"   Time: {result['execution_time']:.2f}s")

    agent.close()

    if all_passed:
        print("\n✅ ALL QUERIES EXECUTED SUCCESSFULLY")
    else:
        print("\n❌ SOME QUERIES FAILED TO EXECUTE")

    return all_passed


def main():
    """Run all SQL syntax tests"""
    print("\n" + "🧪"*40)
    print("  SQL SYNTAX VALIDATION TEST SUITE")
    print("  Verifying 100% Valid SQL Generation")
    print("🧪"*40)

    # Run tests
    test1_passed = test_specific_bug_case()
    test2_passed = test_rule_based_sql_generation()
    test3_passed = test_sql_execution()

    # Final summary
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)

    print(f"\n1. Specific Bug Case: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"2. Rule-Based Generation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"3. SQL Execution: {'✅ PASSED' if test3_passed else '❌ FAILED'}")

    all_passed = test1_passed and test2_passed and test3_passed

    if all_passed:
        print("\n" + "="*80)
        print("  ✅ 100% SUCCESS - ALL SQL SYNTAX TESTS PASSED")
        print("  Bug is FIXED - SQL generation now produces valid syntax")
        print("="*80)
        return True
    else:
        print("\n" + "="*80)
        print("  ❌ TESTS FAILED - SQL syntax issues remain")
        print("="*80)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
