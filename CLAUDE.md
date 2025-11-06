# CLAUDE.md

This file provides guidance to Claude Code when working with this AI AML Agent repository.

## Project Overview

AI AML Agent is a browser automation system for AML (Anti-Money Laundering) verification workflows.

- **LLM**: Llama 4 Maverick via Together.AI for decision making
- **Browser**: Playwright (Python) for headless Chrome automation
- **Language**: Pure Python 3.14 with JIT compiler support

## Development Commands

**Full setup and testing instructions**: See [TESTING.md](TESTING.md)

### Quick Reference

```bash
# Setup (first time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Configure environment
cp .env.example .env  # Add TOGETHER_API_KEY
direnv allow          # Auto-load .env

# Run tests
source venv/bin/activate
python test_amazon_real.py
```

### Client Onboarding

```bash
# 1. Client provides requirements markdown
# See: clients/requirements/TEMPLATE.md

# 2. Generate test script and config
python onboard_client.py clients/requirements/new_client.md

# 3. Debug with Claude Code until stable
python clients/<client_id>/test_<client_id>.py

# 4. When stable, enable for production
```

## Code Architecture

### Core Modules

- **playwright_client.py** - Headless browser automation (async + sync APIs)
- **onboard_client.py** - Client onboarding tool
- **together_ai/** - Llama 4 (Together.AI) client library
- **test_amazon_real.py** - Working example (Amazon shopping flow)
- **test_playwright_llama.py** - Integration tests

### Client Onboarding Workflow

1. Client provides requirements in markdown (see `clients/requirements/TEMPLATE.md`)
2. Run `onboard_client.py` to generate test script and config
3. Debug iteratively with Claude Code until workflow is stable
4. Enable for production when reliable

## Key Patterns

### Async Playwright Pattern

```python
from playwright_client import PlaywrightClient
from together_ai.togetherai import TogetherAIClient

async def main():
    llm = TogetherAIClient(api_key=os.getenv('TOGETHER_API_KEY'))

    async with PlaywrightClient(headless=True) as browser:
        # Navigate
        await browser.navigate("https://example.com")

        # Dynamic selector discovery
        selector = await browser.evaluate("""
            (() => {
                const el = document.querySelector('#search');
                return el ? '#search' : null;
            })()
        """)

        # Take screenshot with metadata
        await browser.screenshot(
            "homepage",
            path=Path("./screenshots/homepage.png"),
            save_metadata=True  # Creates .json file with URL, timestamp
        )

        # Interact
        await browser.fill(selector, "search term")
        await browser.click("#submit")
```

### Llama 4 Decision Making

```python
# Ask Llama 4 to make decisions
response = llm.chat_completion(
    messages=[{"role": "user", "content": prompt}],
    model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    temperature=0.1,  # Low for deterministic navigation
    max_tokens=500
)

decision = response.choices[0].message.content
```

### Screenshot + Metadata Pattern

Every screenshot automatically creates:
- **PNG file** - Visual capture
- **JSON file** - Metadata with URL, timestamp, page title, viewport

```json
{
  "screenshot_name": "01_homepage",
  "url": "https://www.amazon.com/",
  "page_title": "Amazon.com. Spend less. Smile more.",
  "timestamp": "2025-11-06T04:41:55.695357+00:00",
  "viewport": {"width": 1280, "height": 800},
  "browser": "chromium",
  "headless": true
}
```

This satisfies AML compliance requirements for 7-year retention with audit trail.

## Environment & Secrets

- `.env` - Together.AI API key for local development
- `TOGETHER_API_KEY` - Required environment variable
- `PYTHON_JIT=1` - Optional for Python 3.14 JIT performance boost

## Code Standards

- **Python**: Standard formatting, async/await for Playwright
- **Async patterns**: Use `async with PlaywrightClient()` context manager
- **Screenshots**: Always include metadata (`save_metadata=True`)
- **Selectors**: Use dynamic discovery via `browser.evaluate()` when selectors may change

## Claude Guidelines

### General

- Never over-engineer - only do exactly what was asked
- Keep implementations concise and focused
- Use existing patterns from working examples (test_amazon_real.py)
- Add comments instead of creating single-use helper functions

### Client Onboarding Workflow

When user says "debug the new client":
1. Run the test script
2. Identify errors (selector not found, timeout, etc.)
3. Fix the issue (update selectors, add waits, etc.)
4. Run again to verify
5. Repeat until stable and reliable

### Working with Selectors

Selectors on websites change frequently. Always use dynamic discovery:

```python
# ✅ GOOD - Dynamic discovery with fallbacks
selector = await browser.evaluate("""
    (() => {
        const selectors = ['#search', '#main-search', 'input[name="q"]'];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) return sel;
        }
        return null;
    })()
""")

# ❌ BAD - Hardcoded selector
await browser.fill("#search", "query")  # Will break when Amazon changes
```

### Error Handling

When selectors fail:
- Use `browser.evaluate()` to find elements dynamically
- Try multiple selector strategies (ID, class, aria-label, text content)
- Add reasonable waits with `await asyncio.sleep()`
- Use JavaScript click for stubborn elements: `element.click()` in evaluate

## Web Search & Research

**REQUIRED for:**
1. Playwright API changes or new features
2. Together.AI API updates
3. Python 3.14 JIT compiler features
4. Security best practices
5. Any unfamiliar territory

**Search patterns:**
- "Playwright Python [feature] 2025"
- "Together AI Llama 4 [issue] current"
- "Python 3.14 JIT performance"

## Testing Workflow

### Test Stability

Run tests multiple times to verify reliability:

```bash
# Run 3 times to verify consistency
python test_amazon_real.py
python test_amazon_real.py
python test_amazon_real.py
```

All runs should pass with same flow.

### Debugging Failed Tests

Common issues:
- **Timeout**: Selector wrong or element not visible → Use dynamic discovery
- **Click failed**: Element not clickable → Try `evaluate()` with JavaScript click
- **Navigation timeout**: Use `wait_until="load"` instead of `"networkidle"`
- **Screenshot issues**: Check path exists and permissions

## File Organization

```
ai_aml_agent/
├── playwright_client.py          # Browser automation (core)
├── onboard_client.py             # Client onboarding tool
├── test_amazon_real.py           # Working example
├── test_playwright_llama.py      # Integration tests
├── together_ai/                  # Llama 4 client
├── clients/
│   └── requirements/             # Client requirement templates
│       ├── TEMPLATE.md           # Template for clients
│       └── amazon_example.md     # Working example
├── test_screenshots/             # Auto-generated screenshots + JSON
├── README.md                     # Quick start
├── ONBOARDING.md                 # Client onboarding process
└── requirements.txt              # Dependencies
```

## Complex Task Workflow

For multi-step client debugging:

1. Run the test script
2. Note all errors
3. Outline fixes needed
4. Implement fixes one by one
5. Test after each fix
6. Verify stability with multiple runs

Don't plan too much upfront - iterate and fix errors as they appear.
