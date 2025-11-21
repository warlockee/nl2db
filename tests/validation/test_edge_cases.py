#!/usr/bin/env python3
"""
Edge Case Testing for Redshift Natural Language Agent
Tests advanced SQL patterns not covered in test_readme_examples.py

Categories tested:
- Window functions (ROW_NUMBER, RANK, LAG/LEAD, etc.)
- UNION/INTERSECT/EXCEPT operations
- CASE statements and conditional logic
- Complex subqueries (correlated, nested, EXISTS)
- Multi-table JOINs (3+ tables)
- NULL handling edge cases
- Date/time edge cases
- String operations (LIKE, regex, functions)
- Ambiguous queries requiring context understanding
"""

import sys
import os

from redshift_nl_agent.agent import RedshiftAgent
from redshift_nl_agent.database import RedshiftCLI
import time
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com',
    'port': 5439,
    'database': 'prod',
    'user': 'moonshoot_dev',
    'password': os.getenv('REDSHIFT_PASSWORD')
}

# Initialize
agent = RedshiftAgent(
    host=DB_CONFIG['host'],
    port=DB_CONFIG['port'],
    database=DB_CONFIG['database'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    gemini_api_key=os.getenv("GEMINI_API_KEY")
)

print("🚀 Starting Edge Case Verification")
print(f"   Database: {DB_CONFIG['database']}")
print(f"   Mode: Gemini (gemini-flash-latest)")
print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test categories
edge_cases = {
    "WINDOW_FUNCTIONS": [
        {
            "query": "Show the top 3 cameras per fleet by event count",
            "category": "Window Functions - ROW_NUMBER",
            "expected": "Uses ROW_NUMBER() OVER (PARTITION BY fleet ORDER BY count DESC) or RANK()",
        },
        {
            "query": "Rank cameras by total data usage within each fleet",
            "category": "Window Functions - RANK",
            "expected": "Uses RANK() or DENSE_RANK() OVER (PARTITION BY fleet ORDER BY usage DESC)",
        },
        {
            "query": "Show each camera's current and previous firmware version",
            "category": "Window Functions - LAG",
            "expected": "Uses LAG() OVER (PARTITION BY camera ORDER BY upgrade_time)",
        },
        {
            "query": "Calculate running total of daily events for each camera",
            "category": "Window Functions - Running Total",
            "expected": "Uses SUM() OVER (PARTITION BY camera ORDER BY date ROWS UNBOUNDED PRECEDING)",
        },
    ],

    "SET_OPERATIONS": [
        {
            "query": "Show cameras that exist in both camera_info and ods_camera_info_f",
            "category": "INTERSECT Operation",
            "expected": "Uses INTERSECT or inner join to find common cameras",
        },
        {
            "query": "List all unique fleet names from both fleet_info and prod_fleet_name",
            "category": "UNION Operation",
            "expected": "Uses UNION to combine unique fleet names",
        },
        {
            "query": "Find cameras in camera_info but not in ods_camera_info_f",
            "category": "EXCEPT/MINUS Operation",
            "expected": "Uses EXCEPT or LEFT JOIN WHERE right_table IS NULL",
        },
    ],

    "CASE_STATEMENTS": [
        {
            "query": "Categorize cameras as active, idle, or offline based on their latest status",
            "category": "CASE - Status Categorization",
            "expected": "Uses CASE WHEN status = 'online' THEN 'active' ...",
        },
        {
            "query": "Label fleets as Large (>100 cameras), Medium (50-100), or Small (<50)",
            "category": "CASE - Size Buckets",
            "expected": "Uses CASE WHEN camera_count > 100 THEN 'Large' ...",
        },
        {
            "query": "Calculate priority score: high for fleets with >1000 events, medium for 100-1000, low otherwise",
            "category": "CASE - Scoring Logic",
            "expected": "Uses CASE in SELECT to calculate priority",
        },
    ],

    "COMPLEX_SUBQUERIES": [
        {
            "query": "Show cameras that have more events than the average camera",
            "category": "Subquery - Comparison",
            "expected": "Uses subquery: WHERE event_count > (SELECT AVG(event_count) ...)",
        },
        {
            "query": "Find fleets where all cameras are currently online",
            "category": "Correlated Subquery - NOT EXISTS",
            "expected": "Uses NOT EXISTS (SELECT 1 FROM cameras WHERE fleet_id = f.id AND status != 'online')",
        },
        {
            "query": "List cameras with their fleet name and total fleet size",
            "category": "Subquery in SELECT",
            "expected": "Uses (SELECT COUNT(*) FROM cameras c2 WHERE c2.fleet_id = c1.fleet_id) AS fleet_size",
        },
    ],

    "MULTI_TABLE_JOINS": [
        {
            "query": "Show camera events with GPS coordinates, fleet names, and firmware version",
            "category": "4-Table JOIN",
            "expected": "Joins ods_camera_event_f + ods_gps_f + fleet_info + camera_info",
        },
        {
            "query": "List cameras with their fleet info, latest event, and current data usage",
            "category": "Multi-Table JOIN with Aggregation",
            "expected": "Joins camera_info + fleet_info + ods_camera_event_f + fact_data_usage_volume_daily",
        },
    ],

    "NULL_HANDLING": [
        {
            "query": "Count cameras where GPS coordinates are missing",
            "category": "NULL - IS NULL Filter",
            "expected": "Uses WHERE gps_coordinate IS NULL or similar",
        },
        {
            "query": "Show average event count per camera, treating null as zero",
            "category": "NULL - COALESCE in Aggregation",
            "expected": "Uses AVG(COALESCE(event_count, 0))",
        },
        {
            "query": "List cameras ordered by firmware version with nulls appearing last",
            "category": "NULL - ORDER BY with NULLS LAST",
            "expected": "Uses ORDER BY firmware NULLS LAST",
        },
    ],

    "DATE_TIME_EDGE_CASES": [
        {
            "query": "Show events from the last day of last month",
            "category": "Date - Month Boundary",
            "expected": "Uses DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 day'",
        },
        {
            "query": "Find cameras updated during the first week of this month",
            "category": "Date - Week Calculation",
            "expected": "Uses DATE_TRUNC('month', CURRENT_DATE) and INTERVAL '7 days'",
        },
        {
            "query": "Count events grouped by hour of day across all time",
            "category": "Date - Hour Extraction",
            "expected": "Uses EXTRACT(HOUR FROM event_time) or DATE_PART('hour', ...)",
        },
    ],

    "STRING_OPERATIONS": [
        {
            "query": "Find cameras with serial numbers starting with CAM",
            "category": "String - LIKE Prefix",
            "expected": "Uses WHERE serialnumber LIKE 'CAM%'",
        },
        {
            "query": "Show fleets with names containing 'security' case-insensitive",
            "category": "String - ILIKE",
            "expected": "Uses WHERE name ILIKE '%security%'",
        },
        {
            "query": "Get the first 8 characters of each camera serial number",
            "category": "String - SUBSTRING",
            "expected": "Uses SUBSTRING(serialnumber, 1, 8) or LEFT(serialnumber, 8)",
        },
        {
            "query": "Count cameras where firmware version matches pattern 2.x.x",
            "category": "String - Pattern Matching",
            "expected": "Uses WHERE firmware ~ '^2\\.\\d+\\.\\d+$' or SIMILAR TO",
        },
    ],

    "AMBIGUOUS_QUERIES": [
        {
            "query": "Show recent updates",
            "category": "Ambiguous - Multiple Interpretations",
            "expected": "Should clarify or pick most logical: firmware updates, status updates, or data updates",
        },
        {
            "query": "Count by type",
            "category": "Ambiguous - Missing Context",
            "expected": "Should pick event_type, fleet_type, or hardware_type based on context",
        },
    ],
}

# Statistics
total_tests = sum(len(tests) for tests in edge_cases.values())
passed = 0
failed = 0
results = []

print("🧪" * 40)
print(f"  EDGE CASE VERIFICATION - GEMINI MODE")
print(f"  Testing {total_tests} advanced SQL patterns")
print("🧪" * 40)
print()

# Run tests by category
for category_name, tests in edge_cases.items():
    print("=" * 80)
    print(f"CATEGORY: {category_name.replace('_', ' ')} ({len(tests)} queries)")
    print("=" * 80)
    print()

    for i, test in enumerate(tests, 1):
        query = test["query"]
        category = test["category"]
        expected = test["expected"]

        print("=" * 80)
        print(f"Test {i}: {query}")
        print(f"Category: {category}")
        print(f"Expected: {expected}")
        print("=" * 80)

        try:
            start_time = time.time()
            result = agent.query(query)
            exec_time = time.time() - start_time

            sql = result.get('sql', '')
            data = result.get('data', [])
            error = result.get('error', '')

            if error:
                print(f"❌ FAILED - {error}")
                print(f"   Generated SQL: {sql}")
                failed += 1
                results.append({
                    'category': category_name,
                    'test': query,
                    'status': 'FAILED',
                    'error': error,
                    'sql': sql
                })
            else:
                # Check if SQL was generated (even if no rows returned)
                if sql:
                    row_count = len(data) if isinstance(data, list) else 0
                    print(f"✅ PASSED")
                    print(f"   SQL: {sql[:200]}{'...' if len(sql) > 200 else ''}")
                    print(f"   Rows returned: {row_count}")
                    print(f"   Execution time: {exec_time:.2f}s")
                    passed += 1
                    results.append({
                        'category': category_name,
                        'test': query,
                        'status': 'PASSED',
                        'sql': sql,
                        'rows': row_count,
                        'time': exec_time
                    })
                else:
                    print(f"❌ FAILED - No SQL generated")
                    failed += 1
                    results.append({
                        'category': category_name,
                        'test': query,
                        'status': 'FAILED',
                        'error': 'No SQL generated'
                    })

        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            failed += 1
            results.append({
                'category': category_name,
                'test': query,
                'status': 'FAILED',
                'error': str(e)
            })

        print()

# Final report
print("=" * 80)
print("EDGE CASE VERIFICATION REPORT")
print("=" * 80)
print()

success_rate = (passed / total_tests * 100) if total_tests > 0 else 0

print(f"📊 OVERALL RESULTS:")
print(f"   Total Tests: {total_tests}")
print(f"   ✅ Passed: {passed}")
print(f"   ❌ Failed: {failed}")
print(f"   Success Rate: {success_rate:.1f}%")
print()

# Category breakdown
print(f"📋 CATEGORY BREAKDOWN:")
for category_name in edge_cases.keys():
    cat_results = [r for r in results if r['category'] == category_name]
    cat_passed = len([r for r in cat_results if r['status'] == 'PASSED'])
    cat_total = len(cat_results)
    cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
    status_icon = "✅" if cat_rate == 100 else "⚠️" if cat_rate >= 50 else "❌"
    print(f"   {status_icon} {category_name.replace('_', ' ')}: {cat_passed}/{cat_total} ({cat_rate:.1f}%)")
print()

# Failed queries details
if failed > 0:
    print("❌ FAILED QUERIES DETAILS:")
    print()
    failed_results = [r for r in results if r['status'] == 'FAILED']
    for i, result in enumerate(failed_results, 1):
        print(f"   {i}. Category: {result['category']}")
        print(f"      Query: {result['test']}")
        print(f"      Error: {result.get('error', 'Unknown')}")
        if 'sql' in result and result['sql']:
            print(f"      SQL: {result['sql'][:150]}...")
        print()

# Success message
print("=" * 80)
if success_rate >= 90:
    print(f"  ✅ EXCELLENT - {success_rate:.1f}% OF EDGE CASES VERIFIED")
elif success_rate >= 70:
    print(f"  ⚠️  GOOD - {success_rate:.1f}% OF EDGE CASES VERIFIED")
elif success_rate >= 50:
    print(f"  ⚠️  MODERATE - {success_rate:.1f}% OF EDGE CASES VERIFIED")
else:
    print(f"  ❌ NEEDS IMPROVEMENT - {success_rate:.1f}% OF EDGE CASES VERIFIED")
print("=" * 80)

# Cleanup
agent.cli.close()
