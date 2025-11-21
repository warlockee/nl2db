#!/usr/bin/env python3
"""
Redshift Agent - Natural Language to SQL Query Interface
Converts natural language queries to SQL and executes them on Redshift
"""
import re
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .database import RedshiftCLI
from .schema import SchemaContext


class RedshiftAgent:
    """
    Natural Language interface for Redshift queries
    Uses LLM to convert NL to SQL and executes safely
    """

    def __init__(self, host, port, database, user, password, anthropic_api_key=None, gemini_api_key=None):
        """
        Initialize the Redshift Agent

        Args:
            host: Redshift host
            port: Redshift port
            database: Database name
            user: Database user
            password: Database password
            anthropic_api_key: Anthropic API key (optional)
            gemini_api_key: Google Gemini API key (optional)
        """
        self.cli = RedshiftCLI(host, port, database, user, password)
        self.schema_context = SchemaContext(self.cli)
        self.query_history = []
        self.max_rows = 1000
        self.anthropic_api_key = anthropic_api_key
        self.gemini_api_key = gemini_api_key
        self.sql_cache = {}

        # Try to import Gemini
        try:
            import google.generativeai as genai
            self.genai = genai
            self.has_gemini = True
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
        except ImportError:
            self.has_gemini = False

        # Try to import Anthropic
        try:
            import anthropic
            self.anthropic = anthropic
            self.has_anthropic = True
        except ImportError:
            self.has_anthropic = False

        # Determine which LLM to use
        if not self.has_gemini and not self.has_anthropic:
            print("Warning: No LLM packages installed. Using rule-based SQL generation.")
            print("Install with: pip install google-generativeai  OR  pip install anthropic")
        elif self.gemini_api_key and self.has_gemini:
            print("Using Google Gemini for SQL generation")
        elif self.anthropic_api_key and self.has_anthropic:
            print("Using Anthropic Claude for SQL generation")
        else:
            print("Using rule-based SQL generation (no API keys provided)")

    def query(self, natural_language: str, explain: bool = False, format: str = 'table') -> Dict[str, Any]:
        """
        Execute a natural language query

        Args:
            natural_language: Natural language query string
            explain: If True, return SQL without executing
            format: Output format ('table', 'json', 'csv')

        Returns:
            Dict with keys: sql, results, error, execution_time
        """
        start_time = datetime.now()

        try:
            # Check cache first
            if natural_language in self.sql_cache:
                print(f"⚡ Using cached SQL for: '{natural_language}'")
                sql = self.sql_cache[natural_language]
            else:
                # Generate SQL from natural language
                sql = self._generate_sql(natural_language)
                # Cache the result
                self.sql_cache[natural_language] = sql

            if explain:
                return {
                    'sql': sql,
                    'results': None,
                    'error': None,
                    'execution_time': None
                }

            # Validate SQL for safety
            if not self._validate_sql(sql):
                return {
                    'sql': sql,
                    'results': None,
                    'error': 'SQL validation failed: Query contains unsafe operations',
                    'execution_time': None
                }

            # Execute query
            results = self._execute_query(sql)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Store in history
            self.query_history.append({
                'natural_language': natural_language,
                'sql': sql,
                'timestamp': datetime.now(),
                'success': not isinstance(results, str) or not results.startswith('Error')
            })

            return {
                'sql': sql,
                'results': results,
                'error': results if isinstance(results, str) and results.startswith('Error') else None,
                'execution_time': execution_time,
                'format': format
            }

        except Exception as e:
            return {
                'sql': None,
                'results': None,
                'error': f"Error: {str(e)}",
                'execution_time': None
            }

    def _generate_sql(self, natural_language: str) -> str:
        """Generate SQL from natural language using LLM or rules"""

        # Priority: Gemini > Anthropic > Rules
        if self.has_gemini and self.gemini_api_key:
            return self._generate_sql_with_gemini(natural_language)
        elif self.has_anthropic and self.anthropic_api_key:
            return self._generate_sql_with_anthropic(natural_language)
        else:
            return self._generate_sql_with_rules(natural_language)

    def _generate_sql_with_gemini(self, natural_language: str) -> str:
        """Use Google Gemini API to generate SQL"""
        try:
            # Build schema context
            print(f"📊 Building schema context...")
            start_time = time.time()
            schema_context = self.schema_context.build_context_for_llm(natural_language)
            schema_time = time.time() - start_time
            print(f"✓ Schema context ready ({schema_time:.2f}s)")

            # Build prompt
            prompt = f"""{schema_context}

## Task
Convert the following natural language query into a SQL query for the Redshift database.

## Requirements
- Generate ONLY the SQL query, no explanations
- Use standard Redshift SQL syntax
- Use proper date/time functions (e.g. DATEADD, DATEDIFF, CURRENT_DATE)
- Limit results to {self.max_rows} rows maximum if not specified
- Do NOT include semicolons at the end

## Natural Language Query
{natural_language}

## SQL Query
"""
            print(f"📊 Prompt Size: {len(prompt)} chars")

            # Use Gemini to generate SQL
            print("🤖 Generating SQL with Gemini...")
            start_time = time.time()
            model = self.genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            gemini_time = time.time() - start_time
            print(f"✓ SQL generated ({gemini_time:.2f}s)")

            sql = response.text.strip()

            # Clean up the SQL
            sql = re.sub(r'^```sql\s*', '', sql)
            sql = re.sub(r'^```\s*', '', sql)
            sql = re.sub(r'```\s*$', '', sql)
            sql = sql.strip()
            sql = sql.rstrip(';')

            return sql

        except Exception as e:
            raise Exception(f"Gemini SQL generation failed: {str(e)}")

    def _generate_sql_with_anthropic(self, natural_language: str) -> str:
        """Use Claude API to generate SQL"""
        try:
            client = self.anthropic.Anthropic(api_key=self.anthropic_api_key)

            # Build schema context
            print(f"📊 Building schema context...")
            start_time = time.time()
            schema_context = self.schema_context.build_context_for_llm(natural_language)
            schema_time = time.time() - start_time
            print(f"✓ Schema context ready ({schema_time:.2f}s)")

            # Build prompt
            prompt = f"""{schema_context}

## Task
Convert the following natural language query into a SQL query for the Redshift database described above.

## Requirements
- Generate ONLY the SQL query, no explanations
- Use standard Redshift SQL syntax
- Include appropriate JOINs if multiple tables are needed
- Use proper date/time functions for temporal queries
- Add appropriate WHERE clauses for filtering
- Include ORDER BY and LIMIT as appropriate
- For "past week", use: WHERE date_column >= CURRENT_DATE - INTERVAL '7 days'
- For "last month", use: WHERE date_column >= CURRENT_DATE - INTERVAL '1 month'
- For "top N", use: ORDER BY ... DESC LIMIT N
- Always limit results to {self.max_rows} rows maximum if not specified
- Do NOT include semicolons at the end

## Natural Language Query
{natural_language}

## SQL Query
"""

            print("🤖 Generating SQL with Claude (claude-3-5-sonnet)...")
            start_time = time.time()
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            claude_time = time.time() - start_time
            print(f"✓ SQL generated ({claude_time:.2f}s)")

            sql = message.content[0].text.strip()

            # Clean up the SQL
            sql = re.sub(r'^```sql\s*', '', sql)
            sql = re.sub(r'^```\s*', '', sql)
            sql = re.sub(r'```\s*$', '', sql)
            sql = sql.strip()
            sql = sql.rstrip(';')

            return sql

        except Exception as e:
            raise Exception(f"LLM SQL generation failed: {str(e)}")

    def _generate_sql_with_rules(self, natural_language: str) -> str:
        """Simple rule-based SQL generation (fallback)"""
        query_lower = natural_language.lower()

        # Check for unsafe operations in natural language
        unsafe_keywords = ['delete', 'drop', 'truncate', 'alter', 'update', 'insert', 'create', 'grant', 'revoke']
        for keyword in unsafe_keywords:
            if keyword in query_lower:
                raise Exception(f"Unsafe operation detected in query: '{keyword}'. Only SELECT queries are allowed.")

        # Determine tables
        relevant_tables = self.schema_context.get_relevant_tables(natural_language)
        if not relevant_tables:
            raise Exception("Could not determine relevant tables for query")

        main_table = relevant_tables[0]

        # Build WHERE clause first (if temporal filter detected)
        where_clause = ""
        if 'past week' in query_lower or 'last week' in query_lower:
            where_clause = " WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'"
        elif 'past month' in query_lower or 'last month' in query_lower:
            where_clause = " WHERE created_at >= CURRENT_DATE - INTERVAL '1 month'"
        elif 'today' in query_lower:
            where_clause = " WHERE created_at >= CURRENT_DATE"

        # Build SQL with proper clause ordering: SELECT -> FROM -> WHERE -> ORDER BY -> LIMIT
        if 'count' in query_lower or 'how many' in query_lower:
            sql = f"SELECT COUNT(*) as count FROM {main_table}{where_clause}"
        elif 'top' in query_lower or 'most' in query_lower:
            # Extract number
            match = re.search(r'top\s+(\d+)|(\d+)\s+most', query_lower)
            limit = int(match.group(1) or match.group(2)) if match else 10
            sql = f"SELECT * FROM {main_table}{where_clause} ORDER BY id DESC LIMIT {limit}"
        else:
            sql = f"SELECT * FROM {main_table}{where_clause} LIMIT 100"

        return sql

    def _validate_sql(self, sql: str) -> bool:
        """
        Validate SQL for safety
        Only allow SELECT queries and CTEs (WITH clauses), block modifications
        """
        sql_upper = sql.upper().strip()

        # Must start with SELECT or WITH (CTEs are safe for read-only)
        if not (sql_upper.startswith('SELECT') or sql_upper.startswith('WITH')):
            return False

        # Block dangerous operations
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
            'INSERT', 'UPDATE', 'GRANT', 'REVOKE', 'EXECUTE'
        ]

        for keyword in dangerous_keywords:
            if re.search(r'\b' + keyword + r'\b', sql_upper):
                return False

        return True

    def _execute_query(self, sql: str):
        """Execute SQL query with safety limits"""
        # Add LIMIT if not present (ensuring proper SQL clause ordering)
        if 'LIMIT' not in sql.upper():
            # LIMIT should come after WHERE/ORDER BY but before other clauses
            # If sql ends with semicolon, insert before it
            sql = sql.rstrip(';').rstrip()
            sql = f"{sql} LIMIT {self.max_rows}"

        print(f"⚡ Executing query on Redshift...")
        # Show first 100 chars of SQL for context
        sql_preview = sql[:100] + '...' if len(sql) > 100 else sql
        print(f"   SQL: {sql_preview}")
        start_time = time.time()
        result = self.cli.execute(sql)
        exec_time = time.time() - start_time

        # Show result info
        if isinstance(result, str) and result.startswith("Error"):
            print(f"✗ Query failed ({exec_time:.2f}s)")
        else:
            row_count = len(result) if isinstance(result, list) else 0
            print(f"✓ Query complete ({row_count} rows, {exec_time:.2f}s)")

        return result

    def explain_last_query(self) -> Optional[Dict]:
        """Get explanation of the last executed query"""
        if not self.query_history:
            return None
        return self.query_history[-1]

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get query history"""
        return self.query_history[-limit:]

    def get_schema_summary(self) -> str:
        """Get database schema summary"""
        return self.schema_context.get_full_schema_summary()

    def close(self):
        """Close database connection"""
        self.cli.close()
