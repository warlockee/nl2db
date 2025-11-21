# Live Demo Guide

## 🎬 Running a Demo

Perfect for showing the Redshift Natural Language Agent to colleagues or in presentations.

---

## 🚀 Quick Demo Script (5 minutes)

### Preparation (30 seconds)

```bash
# Ensure .env is configured
cp config/.env.template .env
nano .env  # Add credentials

# Launch the demo
./start.sh
```

### Demo Flow (4.5 minutes)

#### 1. Introduction (30 seconds)
```
"This is the Redshift Natural Language Agent. You can query our 
Redshift database using plain English. Watch this..."
```

#### 2. Simple Query (30 seconds)
```
redshift> Count cameras
```
**Point out:**
- Instant SQL generation
- Fast execution
- Clean results

#### 3. Show Schema (30 seconds)
```
redshift> /schema
```
**Point out:**
- 120 tables loaded
- Intelligent table selection
- Automatic schema understanding

#### 4. Complex Query (1 minute)
```
redshift> Show me the top 10 fleets by total data usage
```
**Point out:**
- Handles aggregation
- Proper GROUP BY and ORDER BY
- Sorts and limits correctly

#### 5. Time-Based Query (1 minute)
```
redshift> Show me camera events from the past week
```
**Point out:**
- Understands relative time ("past week")
- Generates correct date functions
- Proper WHERE clause

#### 6. Show Generated SQL (30 seconds)
```
redshift> /explain
```
**Point out:**
- Full SQL visibility
- Can copy and modify if needed
- Great for learning SQL

#### 7. Show Query History (30 seconds)
```
redshift> /history
```
**Point out:**
- Tracks all queries
- Easy to repeat queries
- Audit trail

#### 8. Demonstrate Safety (30 seconds)
```
redshift> Delete all cameras
```
**Point out:**
- Dangerous operations blocked
- Only SELECT and WITH allowed
- Production-safe by design

---

## 🎯 Advanced Demo (10 minutes)

For more technical audiences or detailed walkthroughs.

### Part 1: Setup & Architecture (2 minutes)

1. Show the project structure:
```bash
tree -L 2
```

2. Show the .env.template:
```bash
cat config/.env.template
```

3. Explain the architecture:
- Python package with src/ layout
- Multiple AI backends (Gemini, Claude, Rule-based)
- Docker support

### Part 2: AI Backends (3 minutes)

1. Run with Gemini (if GEMINI_API_KEY set):
```
redshift> Show me devices with firmware version 2.0
```

2. Show it understands context:
```
redshift> How many are there?
```

3. Show complex patterns:
```
redshift> What are the top 5 fleets with most offline cameras?
```

### Part 3: Safety & Validation (2 minutes)

1. Test safe queries:
```
redshift> SELECT * FROM camera_info LIMIT 5
redshift> WITH counts AS (SELECT COUNT(*) FROM fleets) SELECT * FROM counts
```

2. Test blocked queries:
```
redshift> DROP TABLE camera_info
redshift> UPDATE cameras SET status='offline'
redshift> INSERT INTO cameras VALUES (...)
```

### Part 4: CLI Features (2 minutes)

1. Schema exploration:
```
redshift> /schema
```

2. Query history:
```
redshift> /history
```

3. SQL explanation:
```
redshift> /explain
```

4. Help system:
```
redshift> /help
```

### Part 5: Development Features (1 minute)

1. Show testing:
```bash
pytest tests/unit/ -v
```

2. Show Docker deployment:
```bash
docker build -t redshift-nl-agent:latest -f docker/Dockerfile .
```

---

## 🎓 Common Demo Scenarios

### Scenario 1: Data Analyst Demo
**Audience**: Business analysts, data scientists

**Focus**: Ease of use, no SQL required

**Queries:**
```
redshift> Show me total data usage by fleet
redshift> Which cameras have been offline for more than 7 days?
redshift> What's the average firmware version across all fleets?
```

### Scenario 2: Engineering Demo
**Audience**: Developers, DevOps, SREs

**Focus**: Safety, architecture, deployment

**Show:**
- Source code structure
- Safety features (SQL validation)
- Docker deployment
- Test suite (11/11 passing)
- Transaction isolation fix

### Scenario 3: Management Demo
**Audience**: Directors, VPs, executives

**Focus**: Business value, production-ready

**Highlight:**
- "Democratizes data access"
- "100% test pass rate"
- "Production-safe SQL validation"
- "Multiple AI backends for redundancy"
- "Fully containerized for easy deployment"

---

## 🎬 Presentation Tips

### Before the Demo
1. ✅ Test everything works
2. ✅ Prepare .env with valid credentials
3. ✅ Clear terminal for clean slate
4. ✅ Have backup queries ready
5. ✅ Test network connectivity

### During the Demo
1. 🗣️ **Talk while typing**: Explain what you're doing
2. 📊 **Show, don't just tell**: Run actual queries
3. ❌ **Demonstrate failures**: Show safety features work
4. ⏸️ **Pause for questions**: Don't rush
5. 🔄 **Be ready to improvise**: Take audience suggestions

### After the Demo
1. 📧 Share documentation links
2. 🔑 Provide setup instructions
3. 💡 Offer to help with implementation
4. 📝 Gather feedback

---

## 📋 Demo Checklist

### Pre-Demo (5 minutes before)
- [ ] .env file configured
- [ ] ./start.sh tested and working
- [ ] Network connection to Redshift confirmed
- [ ] Terminal window sized appropriately
- [ ] Browser ready with docs (if showing)
- [ ] Backup plan if Gemini API is slow

### Post-Demo
- [ ] Answer questions
- [ ] Share quick start guide
- [ ] Provide access to repository
- [ ] Schedule follow-up if needed

---

## 🎥 Recording a Demo Video

### Setup
```bash
# Use asciinema for terminal recording
asciinema rec demo.cast

# Or use screen recording software
# OBS Studio (free, cross-platform)
```

### Script for Video
1. Show title slide (5 sec)
2. Quick intro (15 sec)
3. Run ./start.sh (10 sec)
4. 3-4 example queries (90 sec)
5. Show /help and commands (30 sec)
6. Closing thoughts (10 sec)

**Total**: ~2.5 minutes (perfect for social media)

---

## 💡 Troubleshooting During Demos

### If Gemini API is slow:
```bash
# Restart with rule-based mode (no API key)
unset GEMINI_API_KEY
./start.sh --python
```

### If connection fails:
- Check .env credentials
- Verify security group rules
- Have backup queries ready from test suite

### If SQL generation fails:
- Use simpler queries
- Show /explain to see what SQL was attempted
- Demonstrate error handling works

---

## 🌟 Best Practices

1. **Keep it simple first**: Start with "count cameras"
2. **Build complexity gradually**: Don't jump to JOINs immediately
3. **Show real value**: Use actual business questions
4. **Be honest about limitations**: Rule-based mode is limited
5. **Emphasize safety**: Highlight the SQL validation

---

**Ready to demo?** Run `./start.sh` and impress your audience! 🎭
