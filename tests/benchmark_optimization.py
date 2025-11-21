import time
import os
import sys
from redshift_nl_agent.agent import RedshiftAgent

def benchmark():
    print("🚀 Starting Benchmark...")
    
    # Measure Init Time
    start = time.time()
    HOST = "daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com"
    PORT = 5439
    DATABASE = "prod"
    USER = "moonshoot_dev"
    PASSWORD = os.getenv("REDSHIFT_PASSWORD")
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    
    agent = RedshiftAgent(HOST, PORT, DATABASE, USER, PASSWORD, gemini_api_key=GEMINI_KEY)
    init_time = time.time() - start
    print(f"⏱️  Initialization Time: {init_time:.4f}s")

    # Measure Query Time (Cold Cache if applicable, but here it's just first run)
    query = "How many fleets do we have?"
    print(f"\n📝 Query: {query}")
    start = time.time()
    result = agent.query(query)
    query_time = time.time() - start
    print(f"⏱️  First Query Time: {query_time:.4f}s")
    
    # Measure Query Time (Warm Cache - in memory)
    print(f"\n📝 Query (Warm): {query}")
    start = time.time()
    result = agent.query(query)
    warm_query_time = time.time() - start
    print(f"⏱️  Second Query Time: {warm_query_time:.4f}s")

    # Measure Query Time (Cached SQL - should be instant)
    print(f"\n📝 Query (Cached SQL): {query}")
    start = time.time()
    result = agent.query(query)
    cached_sql_time = time.time() - start
    print(f"⏱️  Third Query Time (Cached SQL): {cached_sql_time:.4f}s")

    agent.close()

if __name__ == "__main__":
    benchmark()
