# Browser Automation Agent

Two self-contained applications for AI-powered browser automation:

1. **Supervised Training** - Pair-train with AI to create workflows
2. **Workflow Runner** - Execute trained workflows autonomously

Built with **browser-use** + **Kimi K2** (via Together.ai)

---

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure API key
cp .env.example .env
# Edit .env and add your TOGETHER_API_KEY
```

Get API key: https://api.together.xyz/settings/api-keys

---

## 1. Supervised Training App

**Train workflows interactively** by pair-programming with an AI agent.

### How It Works

1. Agent attempts task
2. Gets stuck (loops, errors) → Pauses
3. **Asks you**: "I'm stuck. What should I do?"
4. You provide hint: "Click 'Customers' in sidebar"
5. Agent continues with your guidance
6. Success → Saves workflow as YAML

### Usage

```bash
cd supervised

# Train new workflow
python train.py \
  --task-file ../sandbar_simple.txt \
  --name sandbar_review

# Agent will pause when stuck and ask for help
# You provide hints, agent learns
# Workflow saved to: workflows/sandbar_review.yml
```

**Full docs:** [supervised/README.md](supervised/README.md)

---

## 2. Workflow Runner App

**Execute trained workflows** autonomously in production.

### How It Works

1. Loads trained workflow (YAML)
2. Runs autonomously (no interaction)
3. Returns exit code (0=success, 1=failure)

### Usage

```bash
cd runner

# Execute trained workflow
python run.py --workflow ../supervised/workflows/sandbar_review.yml

# ✅ Workflow executed successfully!
```

**Full docs:** [runner/README.md](runner/README.md)

---

## Complete Workflow

```bash
# 1. TRAIN: Create workflow interactively
cd supervised
python train.py --task-file ../sandbar_simple.txt --name sandbar_review
# → You help agent when stuck
# → Workflow saved: workflows/sandbar_review.yml

# 2. TEST: Execute trained workflow
cd ../runner
python run.py --workflow ../supervised/workflows/sandbar_review.yml
# → Runs autonomously
# → Exit 0 if success

# 3. COMMIT: Save working workflow
git add supervised/workflows/sandbar_review.yml
git commit -m "Add trained Sandbar workflow"

# 4. PRODUCTION: Integrate in CI/CD
# Add runner command to pipeline
```

---

## Architecture

### Supervised Training
- **SupervisedAgent** - Wraps browser-use with monitoring
- **Loop Detection** - Detects stuck patterns (repeated actions, errors, scrolling)
- **Interactive Pause** - Blocks and asks user for guidance
- **Workflow Learning** - Documents successful steps + user hints
- **YAML Output** - Reusable workflow files

### Runner
- **Simple Executor** - Loads YAML, runs workflow
- **Autonomous** - No user interaction
- **Production Ready** - Exit codes for automation
- **Stats Tracking** - Success/failure counts

---

## Technology Stack

- **browser-use** (60K+ ⭐) - AI browser automation library
- **Kimi K2** - #1 on BrowseComp benchmark (60.2% accuracy)
- **Together.ai** - OpenAI-compatible LLM API
- **Playwright** - Headless browser (via browser-use)
- **Python 3.13+** - Modern async/await

---

## Project Structure

```
browser_use_agent/
├── agent.py                    # Core BrowserUseAgent (shared)
├── requirements.txt            # Dependencies
├── .env.example                # Config template
│
├── supervised/                 # 🎓 TRAINING APP
│   ├── train.py               # Entry point
│   ├── supervisor.py          # SupervisedAgent class
│   ├── loop_detector.py       # Loop detection
│   ├── workflow_model.py      # Data models
│   ├── workflows/             # Learned workflows (YAML)
│   └── README.md             # Training docs
│
└── runner/                     # ▶️  EXECUTION APP
    ├── run.py                 # Entry point
    └── README.md             # Runner docs
```

---

## Features

### Training Mode (Supervised)
✅ Real-time loop detection
✅ Interactive pause/resume
✅ User guidance collection
✅ Workflow documentation
✅ YAML output format

### Execution Mode (Runner)
✅ Autonomous execution
✅ Production-ready
✅ Exit codes for CI/CD
✅ Success/failure tracking
✅ Re-training support

---

## Documentation

- **[supervised/README.md](supervised/README.md)** - Full training guide
- **[runner/README.md](runner/README.md)** - Full execution guide
- **[supervised/workflows/README.md](supervised/workflows/README.md)** - Workflow format reference

---

## Use Cases

### Development
- Train workflows for new sites
- Iterate until perfect
- Save learned workflows

### Production
- Execute workflows autonomously
- CI/CD integration
- Scheduled automation
- Monitoring & alerting

### Maintenance
- Re-train when sites change
- Update workflows iteratively
- Track success rates

---

## Docker Support

```bash
# Build
docker-compose build

# Train workflow
docker-compose run browser-use-agent bash -c \
  "cd supervised && python train.py --task-file ../sandbar_simple.txt --name sandbar"

# Run workflow
docker-compose run browser-use-agent bash -c \
  "cd runner && python run.py --workflow ../supervised/workflows/sandbar.yml"
```

---

## Why This Architecture?

**Before:** Monolithic workflow system
**After:** Two focused apps

| Aspect | Before | After |
|--------|--------|-------|
| **Code** | 1 large system | 2 small apps |
| **Training** | Manual editing | Interactive with AI |
| **Execution** | Same code path | Dedicated runner |
| **Debugging** | Hard to isolate | Clear separation |
| **Production** | Risky changes | Stable runner |

---

## Examples

### Example 1: Train Sandbar Workflow

```bash
cd supervised
python train.py --task-file ../sandbar_simple.txt --name sandbar_review

# Agent starts, gets stuck scrolling
# 🤔 I'm stuck scrolling 4 times without progress. What should I do?
# You: "Customer list is already visible. Click any row with alert badges"
# 💡 Got it! Continuing...
# ✅ Task completed! Workflow saved.
```

### Example 2: Execute in Production

```bash
cd runner
python run.py --workflow ../supervised/workflows/sandbar_review.yml

# Runs autonomously
# Exit code 0 = success
# Use in cron, CI/CD, etc.
```

---

## Getting Started

1. **Install**: `pip install -r requirements.txt && playwright install chromium`
2. **Configure**: Copy `.env.example` to `.env`, add API key
3. **Train**: `cd supervised && python train.py --task-file ../sandbar_simple.txt --name test`
4. **Run**: `cd runner && python run.py --workflow ../supervised/workflows/test.yml`

---

## License

MIT

---

**Two apps. One goal: Perfect, repeatable browser automation.**
