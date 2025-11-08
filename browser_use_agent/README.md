# Browser-Use Agent - Kimi K2 + Together.ai Browser Automation

**Production-ready** browser automation agent using:
- **Browser-Use** (60K+ ⭐, MIT license) - Industry-standard AI browser automation
- **Kimi K2** via Together.ai (OpenAI-compatible API) - #1 on BrowseComp (60.2%)
- **Workflow system** with audit trails for compliance

## Why Browser-Use?

This implementation **replaces** the custom MCP approach with a purpose-built library:
- ✅ **75% less code** (138 lines vs 560+ in MCP version)
- ✅ **Simpler Docker** (no Node.js, no MCP servers)
- ✅ **Built-in features**: Screenshots, error recovery, state management
- ✅ **Industry standard**: 60K+ stars, $17M funding, actively maintained

## Quick Start

### 1. Install Dependencies

```bash
cd browser_use_agent
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your TOGETHER_API_KEY
```

Get your Together.ai API key: https://api.together.xyz/settings/api-keys

### 3. Run Test Workflow

```bash
python run_workflow.py --workflow test_workflow.txt --tenant test
```

### 4. Run with Docker

```bash
# Build
docker-compose build

# Run test workflow
docker-compose run browser-use-agent --workflow test_workflow.txt --tenant test
```

## Architecture

```
Python Agent (agent.py - 138 lines)
    ↓
Browser-Use Library
    ├─→ ChatOpenAI (Together.ai endpoint)
    │     ↓
    │   Kimi K2 (moonshotai/Kimi-K2-Instruct-0905)
    │
    └─→ Playwright (Chromium)
          ↓
      Browser Automation
```

## Features

### ✅ Autonomous Workflow Execution
- Natural language task descriptions
- Self-correcting with built-in error recovery
- Vision + HTML extraction for precise element detection

### ✅ Audit Trail for Compliance
**Directory Structure:**
```
audit_logs/
  {tenant}/              # e.g., "sandbar"
    {date}/              # e.g., "2025-11-07"
      {workflow}_{session}/
        ├── screenshots/  # Screenshots + metadata
        │   ├── {timestamp}_step_1.png
        │   ├── {timestamp}_step_1.json  # Metadata for step 1
        │   ├── {timestamp}_step_2.png
        │   ├── {timestamp}_step_2.json  # Metadata for step 2
        │   └── ...
        ├── logs/         # Structured JSONL logs
        │   └── {workflow}.jsonl
        └── state/        # Workflow state
            └── workflow_state.json
```

**What Gets Captured:**
- **Screenshots**: PNG files for each step (base64 decoded)
- **Metadata**: JSON file for each step with:
  - URL visited
  - Actions performed (navigate, click, type, etc.)
  - Evaluation/result
  - Duration in seconds
  - Extracted content
- **Logs**: JSONL format with timestamps, events, errors
- **State**: Workflow completion status, iterations, results

**Example Metadata JSON:**
```json
{
  "step": 1,
  "timestamp": "20251107_155905_864",
  "screenshot": "20251107_155905_864_step_1.png",
  "url": "https://example.com",
  "evaluation": "Start",
  "actions": [
    {
      "navigate": {
        "url": "https://example.com",
        "new_tab": false
      }
    }
  ],
  "duration_seconds": 0.0,
  "results": [
    {
      "extracted_content": "🔗 Navigated to https://example.com",
      "is_done": false
    }
  ]
}
```

### ✅ Template Variables
Replace variables in workflow files:
```txt
Navigate to {URL} and login with {EMAIL} and {PASSWORD}
```

### ✅ Together.ai Integration
Uses Together.ai's OpenAI-compatible endpoint:
- **Endpoint**: `https://api.together.xyz/v1`
- **Model**: `moonshotai/Kimi-K2-Instruct-0905`
- **Cost**: $1 input / $3 output per 1M tokens
- **Context**: 256K tokens
- **Performance**: #1 on BrowseComp (60.2% vs GPT-5's 54.9%)

## Configuration

Environment variables (`.env`):

```bash
# Together.ai API (required)
TOGETHER_API_KEY=your_api_key_here
TOGETHER_MODEL=moonshotai/Kimi-K2-Instruct-0905

# Agent Configuration
AGENT_MAX_ITERATIONS=50
AGENT_HEADLESS=true

# Login Credentials (optional - loaded automatically if not passed via CLI)
GOOGLE_LOGIN=your_email@example.com
GOOGLE_PW=your_password

# Audit Configuration
ENVIRONMENT=local  # local = host storage, docker = container storage
```

## Usage

### Command Line

```bash
# Basic workflow
python run_workflow.py --workflow test_workflow.txt --tenant test

# With template variables (loaded from .env via GOOGLE_LOGIN/GOOGLE_PW if not provided)
python run_workflow.py --workflow sandbar.txt --tenant sandbar

# Override .env credentials via CLI
python run_workflow.py \
    --workflow sandbar.txt \
    --tenant sandbar \
    --email user@example.com \
    --password your_password

# Custom variables
python run_workflow.py \
    --workflow custom.txt \
    --var URL=https://app.example.com \
    --var TENANT_NAME=current
```

### Python API

```python
import asyncio
from agent import BrowserUseAgent, AgentConfig

async def main():
    # Load config from environment
    config = AgentConfig.from_env()

    # Create agent
    agent = BrowserUseAgent(config)

    # Run task
    result = await agent.run_task(
        "Navigate to example.com and extract the main heading"
    )

    print(f"Status: {result['status']}")
    print(f"Result: {result['final_result']}")
    print(f"Screenshots: {len(result['screenshots'])}")

asyncio.run(main())
```

## Workflow File Format

Create `.txt` files with step-by-step instructions:

```txt
Complete the login workflow:

## Steps
1. Navigate to https://app.example.com
2. Find the email input and type: {EMAIL}
3. Find the password input and type: {PASSWORD}
4. Click the "Sign in" button
5. Wait for dashboard to load

GOAL_ACHIEVED when you see the dashboard.
```

**Template Variables:**
- `{EMAIL}` - Replaced with `--email` argument or `GOOGLE_LOGIN` from `.env`
- `{PASSWORD}` - Replaced with `--password` argument or `GOOGLE_PW` from `.env`
- `{CUSTOM}` - Replaced with `--var CUSTOM=value`

## How It Works

### Autonomous Loop

1. **Agent receives** natural language task
2. **Browser-Use analyzes** page using vision + HTML
3. **Kimi K2 decides** next action via Together.ai
4. **Playwright executes** browser action
5. **Screenshot captured** (base64 encoded)
6. **Loop continues** until task complete or max iterations

### Error Recovery

- **Built-in**: Browser-Use handles retries automatically
- **Screenshot logging**: Every step captured for debugging
- **State persistence**: Resume workflows after failures

### Screenshot Handling

Browser-Use returns screenshots as **base64 strings**:
1. Captured automatically during execution
2. Returned in `history.screenshots()`
3. Decoded and saved as PNG files
4. Organized by timestamp and step number

## Docker Deployment

### Cross-Platform Support
Uses `platform: linux/amd64` for compatibility with:
- x86_64 / Intel Macs
- ARM64 / M1/M2/M3 Macs
- Linux servers

### Volume Mounting
When `ENVIRONMENT=local`:
- Screenshots saved to **host machine**: `./audit_logs`
- Persists between container runs
- Easy access for debugging

When `ENVIRONMENT=docker`:
- Screenshots stay in container
- Use `docker cp` to extract
- Ready for S3 upload (future)

## Files Overview

**4 core files** (vs. MCP's 10+ files):

| File | Lines | Purpose |
|------|-------|---------|
| `agent.py` | 138 | Browser-Use agent wrapper (vs. MCP's 560+) |
| `workflow.py` | 300 | Workflow execution & audit logging |
| `run_workflow.py` | 190 | CLI runner |
| `Dockerfile` | 25 | Docker image (no Node.js!) |

## Comparison: Browser-Use vs MCP

| Aspect | Browser-Use ✅ | MCP Approach |
|--------|---------------|--------------|
| **Code Complexity** | 138 lines | 560+ lines |
| **Dependencies** | Python only | Python + Node.js |
| **Docker Image** | Python 3.13 + Playwright | Python + Node.js + MCP servers |
| **Setup** | `pip install browser-use` | Install MCP SDK, Playwright MCP, stdio transport |
| **Tool Routing** | Built-in | Manual routing required |
| **Error Recovery** | Built-in | Custom implementation |
| **Screenshots** | Built-in (base64) | Manual extraction from MCP |
| **Maintenance** | Library updates | Custom code maintenance |
| **Community** | 60K+ stars | Custom implementation |

## Troubleshooting

### "TOGETHER_API_KEY not set"
```bash
cp .env.example .env
# Edit .env and add your API key
```

### "Module 'browser_use' not found"
```bash
pip install browser-use
```

### "Playwright browser not installed"
```bash
playwright install chromium
```

### No screenshots captured
- Browser-Use returns screenshots as base64 strings
- Automatically decoded and saved to `audit_logs/{tenant}/{date}/{workflow}_{session}/screenshots/`
- Check logs for "Screenshots captured: N"

### Agent gets stuck in loop
- Check `AGENT_MAX_ITERATIONS` in `.env`
- Default: 50 iterations
- Increase for complex workflows

## State Directory Explained

The `state/` directory contains workflow execution metadata:

**`workflow_state.json`** includes:
- `workflow_name`: Name of the workflow file
- `started_at`: ISO timestamp of execution start
- `completed`: Boolean - was workflow successful?
- `iterations`: Number of agent loop iterations
- `screenshots_captured`: Total screenshots saved
- `errors`: List of any errors encountered
- `result`: Final result from agent execution

**Use cases:**
- **Debugging**: Check iterations and errors if workflow failed
- **Monitoring**: Track how many iterations workflows typically need
- **Resume**: Future feature to resume failed workflows

## Performance

**Typical Performance:**
- Simple tasks (example.com): 3-5 iterations, ~10-15 seconds
- Login flows: 6-8 iterations, ~20-30 seconds
- Complex workflows: 20-40 iterations, ~60-120 seconds

**Per-iteration latency:** 2-5 seconds (depends on Kimi K2 response time via Together.ai)

## Security

- ✅ **API Keys**: Stored in `.env` files (gitignored)
- ✅ **Browser Sandboxing**: Playwright runs in isolated context
- ✅ **Headless Mode**: No UI exposure in production
- ✅ **Template Variables**: Password masking in logs

## References

- **Browser-Use**: https://github.com/browser-use/browser-use
- **Browser-Use Docs**: https://docs.browser-use.com
- **Together.ai**: https://docs.together.ai/
- **Playwright**: https://playwright.dev/python/

## License

MIT (for code in this directory)

---

**Last Updated:** 2025-11-07 (Screenshots fixed ✅, 4 files, 138-line agent)
