# AI AML Agent

Production browser automation with Llama 4 (Together.AI) and Playwright.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure API key
cp .env.example .env
# Edit .env and add your TOGETHER_API_KEY
```

## Test

```bash
# Basic integration test
python test_playwright_llama.py

# Amazon shopping flow (reference example)
python test_amazon_real.py

# Sandbar AML workflow (production client)
source venv/bin/activate
python clients/[sandbar]/test_[sandbar].py
```

**Sandbar Features:**
- Google SSO + 2FA authentication
- Auth state caching (`auth_state.json`)
- Customer filtering (Open Alerts)
- LLM-based decision making (Llama 4 Maverick)
- Keyboard shortcut automation (y/n for decisions, g+c for navigation)
- Full screenshot + metadata audit trail

## Onboard New Client

```bash
# 1. Client provides requirements
# See: clients/requirements/TEMPLATE.md

# 2. Generate test script and config
python onboard_client.py clients/requirements/new_client.md

# 3. Debug with Claude Code until stable
# 4. Enable for production
```

See [ONBOARDING.md](ONBOARDING.md) for full process.

## Performance (Python 3.14 JIT)

```bash
export PYTHON_JIT=1
python test_amazon_real.py
```
