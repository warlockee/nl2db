#!/usr/bin/env python3
"""
Test Redshift Agent with Google Gemini
"""
import sys
import os

from redshift_nl_agent.agent import RedshiftAgent


def print_result(query_text, result):
    """Pretty print query results"""
    print("\n" + "=" * 80)
    print(f"🔍 Query: {query_text}")
    print("=" * 80)

    if result['error']:
        print(f"❌ Error: {result['error']}")
        if result['sql']:
            print(f"\n💡 Generated SQL:\n   {result['sql']}")
        return

    print(f"\n✅ Generated SQL:")
    print(f"   {result['sql']}")
    print(f"\n⏱  Execution time: {result['execution_time']:.3f}s")

    if result['results']:
        if isinstance(result['results'], str):
            print(f"\n📊 Result: {result['results']}")
        else:
            row_count = len(result['results'])
            print(f"\n📊 Results ({row_count} row{'s' if row_count != 1 else ''}):")

            # Display results
            for i, row in enumerate(result['results'][:5], 1):
                row_str = " | ".join(
                    str(val)[:50] + "..." if val and len(str(val)) > 50 else str(val) if val is not None else "NULL"
                    for val in row
                )
                print(f"   {i}. {row_str}")

            if row_count > 5:
                print(f"   ... and {row_count - 5} more rows")
    else:
        print("\n📊 Result: No data returned")


def main():
    """Test Gemini-powered queries"""
    print("\n" + "🤖" * 40)
    print("  REDSHIFT AGENT - GOOGLE GEMINI TEST")
    print("🤖" * 40)

    # Connection details
    HOST = "daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com"
    PORT = 5439
    DATABASE = "prod"
    USER = "moonshoot_dev"
    PASSWORD = os.getenv("REDSHIFT_PASSWORD")
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")

    try:
        print("\n⚙️  Initializing agent with Gemini...")
        agent = RedshiftAgent(HOST, PORT, DATABASE, USER, PASSWORD,
                            gemini_api_key=GEMINI_KEY)
        print(f"✓ Connected to database: {DATABASE}")
        print(f"✓ Loaded {len(agent.schema_context.table_list)} tables")

        # Test 1: Natural language count query
        print("\n" + "=" * 80)
        print("TEST 1: Natural Language Understanding")
        print("=" * 80)

        queries = [
            "How many fleets do we have?",
            "Show me the names of all fleets",
            "What's the total number of cameras in the system?"
        ]

        for query in queries:
            result = agent.query(query)
            print_result(query, result)

        # Test 2: Complex queries
        print("\n" + "=" * 80)
        print("TEST 2: Complex Query Understanding")
        print("=" * 80)

        queries = [
            "Show me the top 5 most recent fleets",
            "List all fleets that have 'secure' or 'security' in their name",
            "Give me fleet information for the last 3 created fleets"
        ]

        for query in queries:
            result = agent.query(query)
            print_result(query, result)

        # Test 3: Aggregation queries
        print("\n" + "=" * 80)
        print("TEST 3: Aggregation & Analysis")
        print("=" * 80)

        queries = [
            "Count how many cameras are there in ods_camera_info_f",
            "Show me distinct hardware versions from camera data"
        ]

        for query in queries:
            result = agent.query(query)
            print_result(query, result)

        # Show query history
        print("\n" + "=" * 80)
        print("QUERY HISTORY")
        print("=" * 80)

        history = agent.get_history(limit=10)
        successful = sum(1 for h in history if h['success'])

        print(f"\n📊 Total queries: {len(history)}")
        print(f"   ✓ Successful: {successful}")
        print(f"   ✗ Failed: {len(history) - successful}")

        print("\n📜 Recent queries:")
        for i, item in enumerate(history[-5:], 1):
            status = "✓" if item['success'] else "✗"
            print(f"   {i}. {status} \"{item['natural_language']}\"")

        # Close connection
        print("\n⚙️  Closing connection...")
        agent.close()
        print("✓ Connection closed")

        print("\n" + "=" * 80)
        print("  ✅ GEMINI TEST COMPLETED")
        print("=" * 80)
        print("\n💡 Gemini successfully converted natural language to SQL!")
        print("   The LLM understood context and generated appropriate queries.\n")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
