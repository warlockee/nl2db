#!/usr/bin/env python3
"""
Interactive CLI for Redshift Natural Language Agent
Provides a REPL interface for querying Redshift with natural language
"""
import sys
import os
from .agent import RedshiftAgent


class RedshiftAgentCLI:
    """Interactive command-line interface for Redshift Agent"""

    def __init__(self, agent):
        self.agent = agent
        self.commands = {
            '/help': self.show_help,
            '/schema': self.show_schema,
            '/history': self.show_history,
            '/explain': self.explain_last,
            '/quit': self.quit,
            '/exit': self.quit,
        }

    def format_table(self, results, sql=None):
        """Format query results as a table"""
        if isinstance(results, str):
            if results.startswith('Error'):
                print(f"\n\033[91m{results}\033[0m")  # Red color for errors
            else:
                print(f"\n{results}")
            return

        if not results or len(results) == 0:
            print("\n\033[93mNo results found\033[0m")  # Yellow
            return

        # Try to use tabulate for pretty tables
        try:
            from tabulate import tabulate

            # Get column names from the query or use generic names
            if sql and 'SELECT' in sql.upper():
                # Try to extract column names from SQL (simplified)
                # In a real implementation, we'd get this from cursor.description
                col_names = [f"col_{i}" for i in range(len(results[0]))]
            else:
                col_names = [f"col_{i}" for i in range(len(results[0]))]

            # Format and print
            print(f"\n{tabulate(results, headers=col_names, tablefmt='psql')}")
            print(f"\n\033[92m({len(results)} row{'s' if len(results) != 1 else ''})\033[0m")  # Green

        except ImportError:
            # Fallback to simple formatting
            print("\n" + "-" * 80)
            for i, row in enumerate(results[:100], 1):  # Limit display to 100 rows
                row_str = " | ".join(str(val) if val is not None else "NULL" for val in row)
                print(f"{i}. {row_str}")
            if len(results) > 100:
                print(f"\n... and {len(results) - 100} more rows")
            print("-" * 80)
            print(f"\n({len(results)} rows)")

    def show_help(self):
        """Display help information"""
        help_text = """
\033[1mRedshift Natural Language Agent - Help\033[0m

\033[1mCommands:\033[0m
  /help              Show this help message
  /schema            Display database schema summary
  /history           Show recent query history
  /explain           Show SQL for the last query
  /quit, /exit       Exit the application

\033[1mExample Queries:\033[0m
  - Show me all events from the past week
  - Count cameras by fleet
  - What are the top 10 devices by data usage?
  - Find cameras with firmware version 2.0
  - Show me GPS data from yesterday
  - List all fleets with more than 100 cameras

\033[1mTips:\033[0m
  - Be specific about time ranges (e.g., "past week", "last 30 days")
  - Mention table names if you know them (e.g., "camera events")
  - Use natural aggregations (e.g., "count", "top 10", "average")
  - Results are limited to 1000 rows by default

\033[1mNote:\033[0m Only SELECT queries are allowed for safety.
"""
        print(help_text)

    def show_schema(self):
        """Display schema summary"""
        print("\n\033[1mDatabase Schema\033[0m")
        print("=" * 80)
        summary = self.agent.get_schema_summary()
        print(summary)

    def show_history(self):
        """Display query history"""
        history = self.agent.get_history(limit=10)
        if not history:
            print("\n\033[93mNo query history yet\033[0m")
            return

        print("\n\033[1mRecent Query History\033[0m")
        print("=" * 80)
        for i, item in enumerate(reversed(history), 1):
            status = "\033[92m✓\033[0m" if item['success'] else "\033[91m✗\033[0m"
            timestamp = item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n{i}. {status} [{timestamp}]")
            print(f"   NL: {item['natural_language']}")
            print(f"   SQL: {item['sql'][:100]}{'...' if len(item['sql']) > 100 else ''}")

    def explain_last(self):
        """Explain the last query"""
        last = self.agent.explain_last_query()
        if not last:
            print("\n\033[93mNo queries executed yet\033[0m")
            return

        print("\n\033[1mLast Query Explanation\033[0m")
        print("=" * 80)
        print(f"\n\033[1mNatural Language:\033[0m\n{last['natural_language']}")
        print(f"\n\033[1mGenerated SQL:\033[0m\n{last['sql']}")
        print(f"\n\033[1mTimestamp:\033[0m {last['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        success_text = '\033[92mYes\033[0m' if last['success'] else '\033[91mNo\033[0m'
        print(f"\033[1mSuccess:\033[0m {success_text}")

    def quit(self):
        """Quit the application"""
        print("\n\033[92mGoodbye!\033[0m\n")
        self.agent.close()
        sys.exit(0)

    def run(self):
        """Main REPL loop"""
        print("\n\033[1m" + "=" * 80)
        print("Redshift Natural Language Agent")
        print("=" * 80 + "\033[0m")
        print("\nType your query in natural language, or /help for commands")
        print("Examples: 'Show me camera events from the past week'")
        print("         'Count devices by fleet'\n")

        while True:
            try:
                # Get user input
                user_input = input("\033[94mNL2DB>\033[0m ").strip()

                if not user_input:
                    continue

                # Check if it's a command
                if user_input.startswith('/'):
                    command = user_input.split()[0].lower()
                    if command in self.commands:
                        self.commands[command]()
                    else:
                        print(f"\033[91mUnknown command: {command}\033[0m")
                        print("Type /help for available commands")
                    continue

                # Execute natural language query
                print("\n\033[90mGenerating SQL...\033[0m")
                result = self.agent.query(user_input)

                if result['error']:
                    print(f"\n\033[91mError: {result['error']}\033[0m")
                    if result['sql']:
                        print(f"\033[90mGenerated SQL: {result['sql']}\033[0m")
                else:
                    print(f"\n\033[90mSQL: {result['sql']}\033[0m")
                    print(f"\033[90mExecution time: {result['execution_time']:.2f}s\033[0m")
                    self.format_table(result['results'], result['sql'])

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type /quit to exit.")
            except EOFError:
                print()
                self.quit()
            except Exception as e:
                print(f"\n\033[91mError: {str(e)}\033[0m")


def main():
    """Main entry point"""
    # Get database connection details from environment
    HOST = os.getenv('REDSHIFT_HOST', 'daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com')
    PORT = int(os.getenv('REDSHIFT_PORT', '5439'))
    DATABASE = os.getenv('REDSHIFT_DATABASE', 'prod')
    USER = os.getenv('REDSHIFT_USER')
    PASSWORD = os.getenv('REDSHIFT_PASSWORD')

    # Validate required database credentials
    if not USER or not PASSWORD:
        print("\n\033[91mError: Database credentials not found\033[0m")
        print("Please set the following environment variables:")
        print("  REDSHIFT_USER")
        print("  REDSHIFT_PASSWORD")
        print("\nOptionally set:")
        print("  REDSHIFT_HOST (default: daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com)")
        print("  REDSHIFT_PORT (default: 5439)")
        print("  REDSHIFT_DATABASE (default: prod)")
        print("\nSee .env.template for a complete example")
        sys.exit(1)

    # Get API keys from environment
    gemini_key = os.getenv('GEMINI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    if not gemini_key and not anthropic_key:
        print("\n\033[93mWarning: No LLM API keys found\033[0m")
        print("Set GEMINI_API_KEY or ANTHROPIC_API_KEY for full NL capabilities")
        print("The agent will use rule-based SQL generation (limited)\n")

    try:
        print("Connecting to Redshift...")
        agent = RedshiftAgent(HOST, PORT, DATABASE, USER, PASSWORD,
                            anthropic_api_key=anthropic_key,
                            gemini_api_key=gemini_key)

        cli = RedshiftAgentCLI(agent)
        cli.run()

    except Exception as e:
        print(f"\n\033[91mFailed to initialize agent: {str(e)}\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
