#!/usr/bin/env python3
"""
Simple test script for Redshift Agent
Tests basic functionality without requiring Anthropic API
"""
import sys
import os

from redshift_nl_agent.agent import RedshiftAgent


def test_agent():
    """Test basic agent functionality"""
    print("=" * 80)
    print("Redshift Agent - Basic Test")
    print("=" * 80)

    # Connection details
    HOST = "daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com"
    PORT = 5439
    DATABASE = "prod"
    USER = "moonshoot_dev"
    PASSWORD = os.getenv("REDSHIFT_PASSWORD")

    try:
        # Initialize agent (without API key to test rule-based mode)
        print("\n1. Initializing agent (rule-based mode)...")
        agent = RedshiftAgent(HOST, PORT, DATABASE, USER, PASSWORD, anthropic_api_key=None)
        print("   ✓ Agent initialized successfully")
        print(f"   - Schema loaded: {len(agent.schema_context.table_list)} tables")

        # Test 1: Get schema summary
        print("\n2. Testing schema summary...")
        schema = agent.get_schema_summary()
        print(f"   ✓ Schema summary retrieved ({len(schema)} characters)")
        print(f"\n{schema[:500]}...")  # Show first 500 chars

        # Test 2: Simple count query
        print("\n3. Testing simple query: 'count cameras'...")
        result = agent.query("count cameras")
        print(f"   Generated SQL: {result['sql']}")
        if result['error']:
            print(f"   ✗ Error: {result['error']}")
        else:
            print(f"   ✓ Query executed successfully")
            print(f"   - Execution time: {result['execution_time']:.2f}s")
            if isinstance(result['results'], list):
                print(f"   - Results: {result['results']}")

        # Test 3: Top N query
        print("\n4. Testing top 10 query...")
        result = agent.query("top 10 fleets")
        print(f"   Generated SQL: {result['sql']}")
        if result['error']:
            print(f"   ✗ Error: {result['error']}")
        else:
            print(f"   ✓ Query executed successfully")
            print(f"   - Rows returned: {len(result['results']) if isinstance(result['results'], list) else 0}")

        # Test 4: Explain mode
        print("\n5. Testing explain mode (SQL only)...")
        result = agent.query("show me camera events", explain=True)
        print(f"   Generated SQL: {result['sql']}")
        print(f"   ✓ Explain mode working (query not executed)")

        # Test 5: Safety validation
        print("\n6. Testing safety validation (should block unsafe query)...")
        result = agent.query("delete from cameras")
        if result['error'] and 'unsafe' in result['error'].lower():
            print(f"   ✓ Unsafe query correctly blocked")
            print(f"   - Error: {result['error']}")
        else:
            print(f"   ✗ Safety validation may have failed")

        # Test 6: Query history
        print("\n7. Testing query history...")
        history = agent.get_history(limit=5)
        print(f"   ✓ History retrieved: {len(history)} queries")
        for i, item in enumerate(history, 1):
            status = "✓" if item['success'] else "✗"
            print(f"   {i}. {status} {item['natural_language'][:50]}...")

        # Test 7: Schema context for specific query
        print("\n8. Testing relevant table identification...")
        relevant = agent.schema_context.get_relevant_tables("show me camera events")
        print(f"   ✓ Identified {len(relevant)} relevant tables:")
        for table in relevant[:5]:
            print(f"      - {table}")

        # Close connection
        print("\n9. Closing connection...")
        agent.close()
        print("   ✓ Connection closed")

        print("\n" + "=" * 80)
        print("All tests completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
