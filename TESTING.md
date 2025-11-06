# Testing Guide

## Setup

This project uses a Python virtual environment (venv) for dependency management.

### Initial Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Chromium browser for Playwright
playwright install chromium
```

### Environment Variables

The project uses direnv to automatically load environment variables from `.env`:

```bash
# Copy example env file
cp .env.example .env

# Add your Together AI API key
# Edit .env and set TOGETHER_API_KEY=your_key_here

# Allow direnv (one-time)
direnv allow
```

## Running Tests

### Amazon Example Test

```bash
# Activate venv first
source venv/bin/activate

# Run test
python test_amazon_real.py
```

This test demonstrates:
- Navigating to Amazon.com
- Searching for products
- Clicking product
- Adding to cart
- Proceeding to checkout
- Stopping at auth page

Screenshots are saved to `test_screenshots/amazon_real/` with JSON metadata.

## Client Tests

### Sandbar (Production Client)

```bash
# Full run (with login)
source venv/bin/activate
python clients/[sandbar]/test_[sandbar].py

# Clean auth cache and re-login
rm -f clients/[sandbar]/auth_state.json
python clients/[sandbar]/test_[sandbar].py
```

**Features:**
- Processes 1 customer with open AML alerts
- Skips already-dispositioned customers automatically
- Cached authentication (saved to `auth_state.json`)
- LLM-based decision making (Clear → Not Match, Review/Investigate → Match)
- Keyboard shortcuts: `y`/`n` (decision), `r` (reason), `d` (details), `g`+`c` (navigate)

**Credentials required in `.env`:**
- `TOGETHER_API_KEY` - Llama 4 API
- `GOOGLE_LOGIN` - Google email for SSO
- `GOOGLE_PW` - Google password

### Onboarding New Clients

```bash
# Generate test from requirements
python onboard_client.py clients/requirements/new_client.md

# Run generated test
python clients/{client_id}/test_{client_id}.py
```

## Development Workflow

1. Always activate venv before running code: `source venv/bin/activate`
2. Install new dependencies: `pip install package_name` then update `requirements.txt`
3. Run tests to verify changes
4. Deactivate when done: `deactivate`

## Directory Structure

```
ai_aml_agent/
├── venv/                          # Virtual environment (gitignored)
├── ai_agent_audit/                # S3-ready audit data (gitignored)
│   └── {tenant_slug}/
│       └── {session_id}/
│           └── screenshots/       # PNGs + JSON metadata
├── test_screenshots/              # Test screenshots (gitignored)
└── clients/
    └── requirements/              # Client workflow definitions
```

## Troubleshooting

**ModuleNotFoundError**: Activate venv first with `source venv/bin/activate`

**Playwright not found**: Run `playwright install chromium` after activating venv

**API key errors**: Check `.env` file has valid `TOGETHER_API_KEY`
