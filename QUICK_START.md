# Quick Start Guide

## 🚀 Fastest Way to Demo

```bash
# 1. Setup (one-time)
cp config/.env.template .env
nano .env  # Add your credentials

# 2. Run
./start.sh
```

That's it! The script handles everything else.

---

## 📝 What start.sh Does

1. **Checks prerequisites**: Python or Docker
2. **Loads credentials**: From .env or environment
3. **Auto-detects method**: Docker (if available) or Python
4. **Installs if needed**: pip install -e . (Python method)
5. **Launches CLI**: Interactive prompt ready to go

---

## 🎯 Interactive Commands

Once the CLI starts:

### Natural Language Queries
```
redshift> Show me the top 10 cameras by data usage
redshift> Count events from the past week
redshift> What are the busiest fleets?
```

### CLI Commands
```
redshift> /help          # Show available commands
redshift> /schema        # Display database tables (120 tables)
redshift> /history       # Show recent query history
redshift> /explain       # Show SQL for last query
redshift> /quit          # Exit application
```

---

## 🔧 Advanced Usage

### Force specific method:
```bash
./start.sh --python      # Use Python even if Docker available
./start.sh --docker      # Use Docker even if Python available
```

### Environment variables (alternative to .env):
```bash
export REDSHIFT_USER=your_user
export REDSHIFT_PASSWORD=your_password
export GEMINI_API_KEY=your_api_key  # Optional
./start.sh
```

### Manual Python method:
```bash
pip install -e .
export REDSHIFT_USER=your_user
export REDSHIFT_PASSWORD=your_password
python -m redshift_nl_agent
```

### Manual Docker method:
```bash
docker build -t redshift-nl-agent:latest -f docker/Dockerfile .
docker run -it --env-file .env redshift-nl-agent:latest
```

---

## 📚 Example Session

```
$ ./start.sh
================================================================================
  Redshift Natural Language Agent - Demo Launcher
================================================================================

Checking prerequisites...

✓ Found .env file, loading environment variables...
✓ Credentials loaded from: .env file
✓ Python 3 found: 3.11.2
✓ Docker found: 24.0.6

Auto-detected: Using Python method

Starting with Python method...

✓ Package installed successfully

Launching Interactive CLI...

Connecting to Redshift...
Loading schema context...
Loaded 120 core tables
Using Google Gemini for SQL generation

================================================================================
Redshift Natural Language Agent
================================================================================

Type your query in natural language, or /help for commands

redshift> Show me the first 10 cameras

Generating SQL...
SQL: SELECT * FROM camera_info LIMIT 10
Execution time: 0.45s

| camera_id  | fleet_id | status  | firmware |
|------------|----------|---------|----------|
| cam_001    | fleet_1  | online  | 2.0.1    |
| cam_002    | fleet_1  | online  | 2.0.1    |
...

(10 rows)

redshift> /quit

Goodbye!
```

---

## ⚠️ Troubleshooting

### "Missing required environment variables"
- Make sure .env file exists: `ls .env`
- Check it has credentials: `cat .env`
- Or export them: `export REDSHIFT_USER=...`

### "Python 3 not found"
- Install Python 3.8+: `python3 --version`
- Or use Docker method: `./start.sh --docker`

### "Docker is not available"
- Install Docker or use Python: `./start.sh --python`

### "Permission denied: ./start.sh"
- Make it executable: `chmod +x start.sh`

### Connection errors
- Check credentials in .env
- Verify network access to Redshift cluster
- Check security group rules

---

## 📖 More Information

- **Full Documentation**: See `README.md`
- **CLI Reference**: See `docs/CLI_REFERENCE.md`
- **Gemini Setup**: See `docs/GEMINI.md`
- **Database Schema**: See `docs/SCHEMA.md`

---

## 🎓 Tips

1. **Use Gemini for best results**: Set `GEMINI_API_KEY` in .env
2. **Start simple**: Try "count cameras" before complex queries
3. **Use /schema**: See all 120 available tables
4. **Use /explain**: Understand the generated SQL
5. **Check /history**: Review your previous queries

---

**Ready to start?** Run `./start.sh` and start querying! 🚀
