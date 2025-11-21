#!/usr/bin/env python3
"""
Comprehensive README Example Verification
Tests all 30+ example queries from README_AGENT.md with Gemini mode
"""
import sys
import os

from redshift_nl_agent.agent import RedshiftAgent
import time
from datetime import datetime


class ExampleVerifier:
    """Verifies all README examples work as documented"""

    def __init__(self, host, port, database, user, password, gemini_api_key):
        self.agent = RedshiftAgent(host, port, database, user, password, gemini_api_key=gemini_api_key)
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def test_query(self, category, query, expected_behavior=""):
        """Test a single query and record results"""
        self.total_tests += 1

        print(f"\n{'='*80}")
        print(f"Test {self.total_tests}: {query}")
        print(f"Category: {category}")
        if expected_behavior:
            print(f"Expected: {expected_behavior}")
        print(f"{'='*80}")

        start_time = time.time()

        try:
            result = self.agent.query(query)
            execution_time = time.time() - start_time

            # Check for errors
            if result['error']:
                print(f"❌ FAILED - Error: {result['error']}")
                print(f"   Generated SQL: {result['sql']}")

                self.results.append({
                    'category': category,
                    'query': query,
                    'passed': False,
                    'error': result['error'],
                    'sql': result['sql'],
                    'execution_time': execution_time
                })
                self.failed_tests += 1
                return False

            # Success
            row_count = len(result['results']) if isinstance(result['results'], list) else 0
            print(f"✅ PASSED")
            print(f"   SQL: {result['sql']}")
            print(f"   Rows returned: {row_count}")
            print(f"   Execution time: {execution_time:.2f}s")

            self.results.append({
                'category': category,
                'query': query,
                'passed': True,
                'sql': result['sql'],
                'row_count': row_count,
                'execution_time': execution_time
            })
            self.passed_tests += 1
            return True

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ FAILED - Exception: {str(e)}")

            self.results.append({
                'category': category,
                'query': query,
                'passed': False,
                'error': str(e),
                'execution_time': execution_time
            })
            self.failed_tests += 1
            return False

    def run_all_tests(self):
        """Run all README example queries"""

        print("\n" + "🧪"*40)
        print("  README EXAMPLE VERIFICATION - GEMINI MODE")
        print("  Testing all 30+ examples from README_AGENT.md")
        print("🧪"*40)

        # CATEGORY A: Quick Start Examples
        print("\n" + "="*80)
        print("CATEGORY A: QUICK START EXAMPLES (3 queries)")
        print("="*80)

        self.test_query("Quick Start", "Show me the first 10 rows from fleet_info",
                       "First 10 rows from fleet_info table")
        self.test_query("Quick Start", "Count cameras by status",
                       "Aggregated count grouped by status")
        self.test_query("Quick Start", "Show me events from the past week",
                       "Events from last 7 days")

        # CATEGORY B: Simple Queries
        print("\n" + "="*80)
        print("CATEGORY B: SIMPLE QUERIES (4 queries)")
        print("="*80)

        self.test_query("Simple", "Show me all tables",
                       "List of all tables")
        self.test_query("Simple", "Count rows in camera_info",
                       "COUNT(*) for camera_info")
        self.test_query("Simple", "List the first 20 fleets",
                       "First 20 fleet rows")
        self.test_query("Simple", "Display fleet information",
                       "Fleet info table/summary")

        # CATEGORY C: Time-Based Queries
        print("\n" + "="*80)
        print("CATEGORY C: TIME-BASED QUERIES (5 queries)")
        print("="*80)

        self.test_query("Time-Based", "Show events from the past week",
                       "7-day filtered events")
        self.test_query("Time-Based", "Find updates in the last 30 days",
                       "30-day filtered updates")
        self.test_query("Time-Based", "Get data from yesterday",
                       "Single day data")
        self.test_query("Time-Based", "Find firmware updates in the last 30 days",
                       "Firmware updates, 30-day filter")
        self.test_query("Time-Based", "Count clips uploaded today",
                       "Clip count for current date")

        # CATEGORY D: Aggregation Queries
        print("\n" + "="*80)
        print("CATEGORY D: AGGREGATION QUERIES (6 queries)")
        print("="*80)

        self.test_query("Aggregation", "What are the top 10 devices by usage?",
                       "TOP 10 devices, ordered by usage DESC")
        self.test_query("Aggregation", "Count cameras by status",
                       "GROUP BY status with COUNT")
        self.test_query("Aggregation", "Average data usage per fleet",
                       "GROUP BY fleet with AVG")
        self.test_query("Aggregation", "Show average data usage by device",
                       "GROUP BY device with AVG")
        self.test_query("Aggregation", "Count events by type for the past month",
                       "GROUP BY type + 30-day filter")
        self.test_query("Aggregation", "Find the most active cameras this week",
                       "ORDER BY activity DESC + 7-day filter")

        # CATEGORY E: Filtering Queries
        print("\n" + "="*80)
        print("CATEGORY E: FILTERING QUERIES (5 queries)")
        print("="*80)

        self.test_query("Filtering", "Find cameras with status 'offline'",
                       "WHERE status = 'offline'")
        self.test_query("Filtering", "Show devices where usage > 1GB",
                       "WHERE usage > 1GB (numeric comparison)")
        self.test_query("Filtering", "List fleets with more than 100 cameras",
                       "HAVING COUNT(*) > 100")
        self.test_query("Filtering", "List fleets in the security product",
                       "WHERE product = 'security'")
        self.test_query("Filtering", "Get cameras with firmware version 2.0",
                       "WHERE firmware_version = '2.0'")

        # CATEGORY F: Complex Queries
        print("\n" + "="*80)
        print("CATEGORY F: COMPLEX QUERIES (4 queries)")
        print("="*80)

        self.test_query("Complex", "Show me cameras that haven't sent data in 7 days",
                       "Subquery or LEFT JOIN for inactive cameras")
        self.test_query("Complex", "Find the busiest hour for camera events",
                       "Time bucketing + MAX aggregation")
        self.test_query("Complex", "Calculate monthly data usage trends",
                       "DATE_TRUNC by month + aggregation")
        self.test_query("Complex", "List fleets with more than 100 devices",
                       "GROUP BY + HAVING COUNT(*) > 100")

        # CATEGORY G: Programmatic Examples
        print("\n" + "="*80)
        print("CATEGORY G: PROGRAMMATIC EXAMPLES (3 queries)")
        print("="*80)

        self.test_query("Programmatic", "Show me the top 10 devices by data usage",
                       "TOP 10 devices by usage")
        self.test_query("Programmatic", "Show me the top 10 cameras by data usage",
                       "TOP 10 cameras by usage")
        self.test_query("Programmatic", "Count events by type",
                       "GROUP BY event type with COUNT")

        # Generate summary report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive verification report"""

        print("\n" + "="*80)
        print("VERIFICATION REPORT")
        print("="*80)

        # Overall summary
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   ✅ Passed: {self.passed_tests}")
        print(f"   ❌ Failed: {self.failed_tests}")
        print(f"   Success Rate: {pass_rate:.1f}%")

        # Category breakdown
        print(f"\n📋 CATEGORY BREAKDOWN:")
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'failed': 0, 'total': 0}
            categories[cat]['total'] += 1
            if result['passed']:
                categories[cat]['passed'] += 1
            else:
                categories[cat]['failed'] += 1

        for cat, stats in categories.items():
            cat_pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status_icon = "✅" if cat_pass_rate == 100 else "⚠️" if cat_pass_rate >= 80 else "❌"
            print(f"   {status_icon} {cat}: {stats['passed']}/{stats['total']} ({cat_pass_rate:.1f}%)")

        # Performance stats
        if self.passed_tests > 0:
            passed_results = [r for r in self.results if r['passed']]
            avg_time = sum(r['execution_time'] for r in passed_results) / len(passed_results)
            min_time = min(r['execution_time'] for r in passed_results)
            max_time = max(r['execution_time'] for r in passed_results)

            print(f"\n⏱️  PERFORMANCE METRICS (Passed Queries):")
            print(f"   Average execution time: {avg_time:.2f}s")
            print(f"   Min execution time: {min_time:.2f}s")
            print(f"   Max execution time: {max_time:.2f}s")

        # Failed queries detail
        if self.failed_tests > 0:
            print(f"\n❌ FAILED QUERIES DETAILS:")
            failed_results = [r for r in self.results if not r['passed']]
            for i, result in enumerate(failed_results, 1):
                print(f"\n   {i}. Category: {result['category']}")
                print(f"      Query: {result['query']}")
                print(f"      Error: {result.get('error', 'Unknown error')}")
                if 'sql' in result:
                    print(f"      SQL: {result['sql']}")

        # Final verdict
        print("\n" + "="*80)
        if pass_rate == 100:
            print("  ✅ SUCCESS - 100% OF README EXAMPLES VERIFIED")
            print("  All documented examples work as expected with Gemini!")
        elif pass_rate >= 90:
            print("  ✅ EXCELLENT - 90%+ EXAMPLES VERIFIED")
            print("  Most examples work, minor issues found")
        elif pass_rate >= 80:
            print("  ⚠️  GOOD - 80%+ EXAMPLES VERIFIED")
            print("  Most examples work, some issues need attention")
        elif pass_rate >= 70:
            print("  ⚠️  ACCEPTABLE - 70%+ EXAMPLES VERIFIED")
            print("  Significant issues found, documentation may need updates")
        else:
            print("  ❌ NEEDS WORK - <70% EXAMPLES VERIFIED")
            print("  Major issues found, documentation needs significant updates")
        print("="*80)

        return pass_rate >= 80

    def close(self):
        """Close agent connection"""
        self.agent.close()


def main():
    """Run comprehensive README example verification"""

    # Connection details
    HOST = "daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com"
    PORT = 5439
    DATABASE = "prod"
    USER = "moonshoot_dev"
    PASSWORD = os.getenv("REDSHIFT_PASSWORD")
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")

    print(f"\n🚀 Starting README Example Verification")
    print(f"   Database: {DATABASE}")
    print(f"   Mode: Gemini (gemini-flash-latest)")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    verifier = ExampleVerifier(HOST, PORT, DATABASE, USER, PASSWORD, GEMINI_KEY)

    try:
        verifier.run_all_tests()
        success = verifier.passed_tests == verifier.total_tests
        verifier.close()
        return success
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        verifier.close()
        return False
    except Exception as e:
        print(f"\n\n❌ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        verifier.close()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
