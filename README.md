# AI AML Agent

**Production-ready** browser automation for AML workflows using Kimi K2 (Together.ai) + Browser-Use.

## 🚀 Quick Start

```bash
cd browser_use_agent

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
# Edit .env and add your TOGETHER_API_KEY

# Test
python run_workflow.py --workflow test_workflow.txt --tenant test
```

**See [`browser_use_agent/README.md`](browser_use_agent/README.md) for full documentation.**

## Architecture

Built with **Browser-Use** (60K+ ⭐, MIT license) - industry-standard AI browser automation library:

- ✅ **138-line agent** - Clean, maintainable implementation
- ✅ **Python only** - No Node.js or external servers
- ✅ **Built-in features** - Screenshots, error recovery, state management
- ✅ **Together.ai** - OpenAI-compatible endpoint for Kimi K2
- ✅ **Audit trails** - Compliance-ready logging and screenshots

## Features

### ✅ Autonomous Workflow Execution
- Natural language task descriptions
- Self-correcting with built-in error recovery
- Vision + HTML extraction for precise element detection

### ✅ Compliance-Ready Audit Trails
```
audit_logs/{tenant}/{date}/{workflow}_{session}/
  ├── screenshots/        # PNG files + JSON metadata for each step
  │   ├── {timestamp}_step_1.png
  │   ├── {timestamp}_step_1.json  # Metadata: URL, actions, duration, results
  │   ├── {timestamp}_step_2.png
  │   ├── {timestamp}_step_2.json
  │   └── ...
  ├── logs/              # JSONL structured logs
  │   └── {workflow}.jsonl
  └── state/             # Workflow execution metadata
      └── workflow_state.json
```

**Metadata includes**: URL, actions performed, evaluation, duration, extracted content

### ✅ Template Variables
```txt
Login to {URL} with {EMAIL} and {PASSWORD}
```

### ✅ Docker Deployment
```bash
cd browser_use_agent
docker-compose build
docker-compose run browser-use-agent --workflow test_workflow.txt --tenant test
```

## Documentation

- **[browser_use_agent/README.md](browser_use_agent/README.md)** - Complete documentation
- **[TODO.md](TODO.md)** - Implementation history
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines

## Performance

**Typical execution times:**
- Simple tasks: 10-15 seconds (3-5 iterations)
- Login flows: 20-30 seconds (6-8 iterations)
- Complex AML workflows: 60-120 seconds (20-40 iterations)

**Cost (Together.ai):**
- ~$0.001 per iteration (Kimi K2)
- ~10x cheaper than GPT-4
- Best on BrowseComp benchmark (60.2% vs GPT-5's 54.9%)

## Project Structure

```
├── browser_use_agent/       # Production implementation
│   ├── agent.py            # 138-line autonomous agent
│   ├── workflow.py         # Workflow execution & audit trails
│   ├── run_workflow.py     # CLI runner
│   ├── Dockerfile          # Docker deployment
│   └── README.md           # Full documentation
├── README.md               # This file
├── TODO.md                 # Implementation history
└── CLAUDE.md              # Development guidelines
```
