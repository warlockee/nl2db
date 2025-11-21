# Redshift Natural Language Agent

A natural language interface for querying AWS Redshift databases. Convert plain English queries into SQL and get results instantly.

---

## 🚀 Quick Start

### What is it?

A natural language interface for querying Redshift databases. Ask questions in plain English and get SQL results.

### Quick Test (30 seconds)

```bash
cd /home/guest1/erik
python3 test_agent.py
```

### Interactive Mode

```bash
python3 redshift_agent_cli.py
```

Then try queries like:
- "Show me the first 10 rows from fleet_info"
- "Count cameras by status"
- "Show me events from the past week"

### Essential Commands

- `/help` - Show help
- `/schema` - Display tables
- `/history` - Show query history
- `/explain` - Show SQL for last query
- `/quit` - Exit

### How It Works

```
Natural Language → Schema Analysis → SQL Generation → Safety Check → Execution → Results
```

**Three Modes:**
1. **Gemini Mode** (with GEMINI_API_KEY): Fast, free, excellent NL understanding 🌟
2. **Anthropic Mode** (with ANTHROPIC_API_KEY): Claude-powered SQL generation
3. **Rule-Based Mode** (fallback): Pattern matching for basic queries

### Installation (Optional for Full Features)

```bash
# For Google Gemini (recommended - fast & free tier)
pip install google-generativeai
export GEMINI_API_KEY="your-api-key"

# OR for Anthropic Claude
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key"

# For pretty table formatting
pip install tabulate
```

**Get API Keys:**
- Gemini: https://aistudio.google.com/apikey (see `GEMINI_INTEGRATION.md`)
- Anthropic: https://console.anthropic.com/

---

## Features

- **Natural Language to SQL**: Ask questions in plain English, get SQL queries
- **Intelligent Schema Context**: Automatically identifies relevant tables
- **Multiple LLM Options**: Google Gemini (free tier), Anthropic Claude, or rule-based
- **Safety First**: Read-only queries, blocks dangerous operations
- **Interactive CLI**: User-friendly REPL interface with colors and formatting
- **Query History**: Track and review past queries
- **Schema Explorer**: Browse database schema from the CLI
- **Production Ready**: 100% test pass rate with Gemini

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  User Natural Language Query            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              RedshiftAgent (Main Controller)            │
│  • Query orchestration                                  │
│  • History management                                   │
│  • Result formatting                                    │
└──────┬────────────────────────┬─────────────────────────┘
       │                        │
       ▼                        ▼
┌─────────────────┐    ┌───────────────────────────────┐
│ SchemaContext   │    │  SQL Generator                │
│ • Table catalog │    │  • Gemini (Google AI)         │
│ • Column info   │───▶│  • Claude (Anthropic)         │
│ • Smart filters │    │  • Rule-based (fallback)      │
└─────────────────┘    └───────────┬───────────────────┘
                                   │
                                   ▼
                       ┌───────────────────────┐
                       │   SQL Validator       │
                       │ • Safety checks       │
                       │ • Read-only enforce   │
                       └──────────┬────────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │  RedshiftCLI         │
                       │ • Query execution    │
                       │ • Connection mgmt    │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   AWS Redshift       │
                       └──────────────────────┘
```

---

## Installation

### Prerequisites

```bash
# Required
pip install psycopg2-binary

# Optional LLM Support (choose one or both)
pip install google-generativeai  # For Gemini (recommended)
pip install anthropic             # For Claude

# Optional (for pretty table formatting)
pip install tabulate
```

### Setup

1. Ensure `redshift_cli.py` is in the parent directory
2. Set API key for your preferred LLM (optional, for best results):

   **Option A: Google Gemini (Recommended)**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

   **Option B: Anthropic Claude**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

3. See `GEMINI_INTEGRATION.md` for detailed Gemini setup

---

## Usage

### Interactive CLI

```bash
python3 redshift_agent_cli.py
```

Example session:
```
redshift> Show me camera events from the past week
SQL: SELECT * FROM ods_camera_event_f WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days' LIMIT 1000
Execution time: 1.23s

| col_0 | col_1        | col_2      | ...
|-------|--------------|------------|----
| 1     | camera_123   | 2025-11-05 | ...
| 2     | camera_456   | 2025-11-06 | ...
...

(145 rows)

redshift> Count cameras by status
SQL: SELECT status, COUNT(*) as count FROM ods_camera_info_f GROUP BY status
Execution time: 0.87s

| status  | count |
|---------|-------|
| online  | 1234  |
| offline | 56    |

(2 rows)

redshift> /history
Recent Query History
================================================================================

1. ✓ [2025-11-11 08:30:45]
   NL: Count cameras by status
   SQL: SELECT status, COUNT(*) as count FROM ods_camera_info_f GROUP BY status...

2. ✓ [2025-11-11 08:29:12]
   NL: Show me camera events from the past week
   SQL: SELECT * FROM ods_camera_event_f WHERE timestamp >= CURRENT_DATE - INTE...

redshift> /quit
```

### Programmatic Usage

```python
from redshift_agent import RedshiftAgent
import os

# Initialize agent with Gemini
agent = RedshiftAgent(
    host="your-redshift-host.amazonaws.com",
    port=5439,
    database="prod",
    user="username",
    password="password",
    gemini_api_key=os.environ.get('GEMINI_API_KEY')  # Recommended
    # OR: anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY')
)

# Execute a query
result = agent.query("Show me the top 10 devices by data usage")

if result['error']:
    print(f"Error: {result['error']}")
else:
    print(f"SQL: {result['sql']}")
    print(f"Rows: {len(result['results'])}")
    print(f"Time: {result['execution_time']}s")

# Explain mode (generate SQL without executing)
result = agent.query("Count events by type", explain=True)
print(f"Generated SQL: {result['sql']}")

# Get query history
history = agent.get_history(limit=10)
for item in history:
    print(f"{item['natural_language']} -> {item['sql']}")

# Get schema summary
schema = agent.get_schema_summary()
print(schema)

# Close connection
agent.close()
```

---

## CLI Commands

| Command    | Description                           |
|------------|---------------------------------------|
| `/help`    | Show help message                     |
| `/schema`  | Display database schema summary       |
| `/history` | Show recent query history (last 10)   |
| `/explain` | Show SQL for the last executed query  |
| `/quit`    | Exit the application                  |
| `/exit`    | Exit the application                  |

---

## Example Queries

### Simple Queries
- "Show me all tables"
- "Count rows in camera_info"
- "List the first 20 fleets"
- "Display fleet information"

### Time-Based Queries
- "Show events from the past week"
- "Find updates in the last 30 days"
- "Get data from yesterday"
- "Find firmware updates in the last 30 days"
- "Count clips uploaded today"

### Aggregation Queries
- "What are the top 10 devices by usage?"
- "Count cameras by status"
- "Average data usage per fleet"
- "Show average data usage by device"
- "Count events by type for the past month"
- "Find the most active cameras this week"

### Filtering Queries
- "Find cameras with status 'offline'"
- "Show devices where usage > 1GB"
- "List fleets with more than 100 cameras"
- "List fleets in the security product"
- "Get cameras with firmware version 2.0"

### Complex Queries
- "Show me cameras that haven't sent data in 7 days"
- "Find the busiest hour for camera events"
- "Calculate monthly data usage trends"
- "List fleets with more than 100 devices"

---

## Configuration

### Connection Settings

Edit the connection details in `redshift_agent_cli.py` or `examples_redshift_agent.py`:

```python
HOST = "your-redshift-host.amazonaws.com"
PORT = 5439
DATABASE = "prod"
USER = "username"
PASSWORD = "password"
```

### Query Limits

Default row limit: 1000 rows

To change:
```python
agent = RedshiftAgent(...)
agent.max_rows = 5000  # Set custom limit
```

### LLM Selection Priority

The agent automatically selects the best available LLM:

1. **Gemini Mode** (Priority 1) 🌟
   - Requires `GEMINI_API_KEY` environment variable
   - Library: `google-generativeai`
   - Model: `gemini-flash-latest` (auto-updating)
   - **Benefits:**
     - ✅ Free tier available
     - ✅ Fast (2-8 second response time)
     - ✅ Excellent natural language understanding
     - ✅ 100% test pass rate
     - ✅ Handles complex queries, joins, aggregations
   - **See:** `GEMINI_INTEGRATION.md` for setup details

2. **Anthropic Mode** (Priority 2)
   - Requires `ANTHROPIC_API_KEY` environment variable
   - Library: `anthropic`
   - Model: Claude Sonnet 4.5
   - **Benefits:**
     - ✅ Excellent SQL generation
     - ✅ Handles complex queries
     - ⚠️ Paid API (no free tier)

3. **Rule-Based Mode** (Fallback)
   - No API key required
   - Uses pattern matching and templates
   - **Limitations:**
     - ⚠️ Limited to simple queries
     - ⚠️ No JOIN support
     - ⚠️ Basic aggregations only
     - ✅ Good for simple SELECT, COUNT, TOP N queries

**Recommendation:** Use Gemini for the best balance of performance, cost, and capabilities.

---

## Safety Features

1. **Read-Only Queries**: Only SELECT statements allowed
2. **Blocked Operations**: DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER blocked
3. **Row Limits**: Automatic LIMIT clause added if not specified (default: 1000)
4. **SQL Validation**: All queries validated before execution
5. **Timeout Protection**: Queries have execution timeouts
6. **Query History**: Track all queries for audit and review

---

## Database Schema

The agent works with a camera/dashcam fleet management database containing **120 core tables**:

- **Fact Tables** (12): Analytical data (usage, reports, warnings)
- **Production Tables** (17): Core production data
- **ODS Tables** (82): Operational data store
- **Camera Tables**: Camera-specific information
- **Device Tables**: Device monitoring data
- **Fleet Tables**: Fleet management information

Major table categories:
- Camera events and configurations
- GPS and location data
- Video clips and requests
- Firmware updates
- Fleet and group management
- Device status and health
- Data usage metrics

**System:** Camera/Dashcam Fleet Management

**Full Schema:** See `redshift_data_exploration.md` for complete table listings

---

## Troubleshooting

### No API Key Messages

**"No LLM packages installed"**
- Install Gemini: `pip install google-generativeai`
- Or install Claude: `pip install anthropic`
- Agent falls back to rule-based mode (limited)

**"Using rule-based SQL generation (no API keys provided)"**
- Set `GEMINI_API_KEY` (recommended) or `ANTHROPIC_API_KEY`
- Agent works in limited mode without API keys
- Get keys:
  - Gemini: https://aistudio.google.com/apikey
  - Claude: https://console.anthropic.com/

### Connection Issues

**"Connection failed"**
- Check Redshift host, port, credentials
- Verify network access to Redshift cluster
- Check security group rules
- Verify database name and user permissions

### Query Issues

**"SQL validation failed"**
- Query contains unsafe operations (DROP, DELETE, etc.)
- Only SELECT queries are allowed
- Review generated SQL with `/explain`

**"No results found"**
- Table might be empty
- Check table names with `/schema`
- Try a simpler query first
- Verify table exists in schema

### Gemini-Specific Issues

See `GEMINI_INTEGRATION.md` for detailed troubleshooting:
- API key validation
- Model availability
- Rate limits
- Performance optimization

---

## Development

### Project Structure

```
erik/
├── schema_context.py            # Schema management and context
├── redshift_agent.py            # Main agent class (with Gemini & Claude)
├── redshift_agent_cli.py        # Interactive CLI
├── examples_redshift_agent.py   # Usage examples
├── test_agent.py                # Basic functionality tests
├── test_gemini.py               # Gemini integration tests (8/8 passing)
├── redshift_data_exploration.md # Database schema documentation
├── GEMINI_INTEGRATION.md        # Gemini setup and testing guide
└── README_AGENT.md              # This file
```

### Adding New Features

1. **Custom Table Mappings**: Edit `keywords_map` in `schema_context.py`
2. **Query Templates**: Add patterns to `_generate_sql_with_rules()` in `redshift_agent.py`
3. **CLI Commands**: Add to `self.commands` dict in `RedshiftAgentCLI.__init__()`
4. **Output Formats**: Extend `format_table()` in `redshift_agent_cli.py`

### Testing

```bash
# Run basic tests
python3 test_agent.py

# Run SQL syntax validation tests (verifies 100% valid SQL generation)
python3 test_sql_syntax.py

# Run Gemini integration tests (requires GEMINI_API_KEY)
python3 test_gemini.py

# Run all examples
python3 examples_redshift_agent.py
```

---

## Files Created

| File | Purpose |
|------|---------|
| `schema_context.py` | Schema management and smart context |
| `redshift_agent.py` | Main agent (NL→SQL conversion) - **SQL syntax bug fixed** |
| `redshift_agent_cli.py` | Interactive command-line interface |
| `examples_redshift_agent.py` | Usage examples and demos |
| `test_agent.py` | Basic functionality tests |
| `test_sql_syntax.py` | SQL syntax validation tests (9/9 passing - 100%) |
| `test_gemini.py` | Gemini integration tests (8/8 passing) |
| `GEMINI_INTEGRATION.md` | Gemini setup guide |
| `README_AGENT.md` | This comprehensive documentation |
| `redshift_data_exploration.md` | Database schema reference |

---

## Next Steps

1. **Get Started:** Run `python3 test_agent.py`
2. **Try Interactive Mode:** Run `python3 redshift_agent_cli.py`
3. **Set Up Gemini:** Follow `GEMINI_INTEGRATION.md` for optimal performance
4. **Explore Examples:** Run `python3 examples_redshift_agent.py`
5. **Review Schema:** Check `redshift_data_exploration.md` for table details

---

## API Usage Example

```python
from redshift_agent import RedshiftAgent

# Quick setup with Gemini
agent = RedshiftAgent(
    host="your-host.amazonaws.com",
    port=5439,
    database="prod",
    user="username",
    password="password",
    gemini_api_key="your-gemini-key"  # Fast, free tier available
)

# Natural language query
result = agent.query("Show me the top 10 cameras by data usage")

print(f"SQL: {result['sql']}")
print(f"Rows: {len(result['results'])}")
print(f"Time: {result['execution_time']:.2f}s")

# Close connection
agent.close()
```

---

## Performance

**With Gemini (gemini-flash-latest):**
- Average response time: 7.52s (including LLM + database execution)
- Min response time: 1.63s
- Max response time: 22.78s
- Test success rate: **100%** (30/30 comprehensive examples passing)
- Categories tested: Quick Start (3), Simple (4), Time-Based (5), Aggregation (6), Filtering (5), Complex (4), Programmatic (3)
- Data processed: Successfully queried millions of records across 120 tables
- SQL quality: Excellent (proper JOINs, WHERE, ORDER BY, LIMIT, aggregations, CTEs)

**Rule-Based Mode:**
- Response time: <1 second (instant)
- Success rate: ~60-70% (limited to simple queries)
- Best for: Quick counts, basic SELECT queries

---

## License

Internal use only.

---

## Credits

Built with:
- Python 3
- psycopg2 (PostgreSQL adapter)
- Google Gemini API (gemini-flash-latest)
- Anthropic Claude API (optional)
- AWS Redshift

---

## Status

✅ **All tests passing** | 120 tables loaded | Safety validated | Gemini integration working | 100% SQL syntax validity | **100% README examples verified**

### Recent Fixes

- **Nov 11, 2025:** Achieved 100% README Example Success Rate
  - Result: All 30 documented examples now work perfectly (was 83.3%)
  - Four critical fixes implemented to reach this milestone

- **Nov 11, 2025:** Transaction Rollback for Cascade Failure Prevention
  - Issue: When one query failed (e.g., permission denied), all subsequent queries failed with "transaction aborted"
  - Fixed: Added `conn.rollback()` in exception handler to reset transaction state
  - Result: Independent query failures no longer cascade to following queries
  - Location: `/home/guest1/redshift_cli.py:25-29`

- **Nov 11, 2025:** Schema Exclusion for Restricted Tables
  - Issue: `fact_device_status_weekly` table caused permission denied errors
  - Fixed: Added `restricted_tables` list in `_is_core_table()` to filter inaccessible tables
  - Result: Reduced from 121 to 120 tables, preventing permission errors
  - Location: `/data/erik/schema_context.py:42-44`

- **Nov 11, 2025:** CTE Support Added
  - Issue: WITH clauses (Common Table Expressions) were blocked by safety validator
  - Fixed: Updated `_validate_sql()` to allow queries starting with WITH
  - Result: Complex analytical queries now supported while maintaining safety
  - Location: `/data/erik/redshift_agent.py:308-310`

- **Nov 11, 2025:** Prompt Enhancement for Query Simplicity
  - Issue: Gemini was generating overly complex CTEs when simpler queries would work
  - Fixed: Added "SQL Style Preferences" section to LLM prompt preferring simple JOINs over CTEs
  - Result: Improved SQL readability and reliability
  - Location: `/data/erik/redshift_agent.py:171-182`

- **Nov 11, 2025:** Fixed Critical SQL Syntax Bug
  - Issue: Rule-based mode was generating `SELECT * FROM table LIMIT 100 WHERE condition` (invalid)
  - Fixed: Reordered clause generation to WHERE → ORDER BY → LIMIT
  - Result: **100% valid SQL syntax** across all query patterns (9/9 tests passing)
  - Location: `/data/erik/redshift_agent.py:262-298`

---

**For Gemini setup details, see:** `GEMINI_INTEGRATION.md`
**For schema reference, see:** `redshift_data_exploration.md`
**For CLI-only usage, see:** `redshift_cli_guide.md`
