# Client Onboarding Process

## Overview

For each new client, follow this process to create a stable, production-ready automation agent.

## Process

### 1. Client provides requirements document

Client sends a markdown file with:
- Website URL
- Workflow steps (what to do)
- Known selectors (if any)
- Special requirements/notes

**Template:** `clients/requirements/TEMPLATE.md`

### 2. Generate initial files

```bash
python onboard_client.py clients/requirements/new_client.md
```

This creates:
- `clients/<client_id>/test_<client_id>.py` - Test script
- `clients/<client_id>/<client_id>.yml` - Configuration

### 3. Debug and iterate with Claude Code

Work with Claude Code (me) to:
- Run test: `python clients/<client_id>/test_<client_id>.py`
- Fix errors (selectors, timing, etc.)
- Update test script until stable
- Run multiple times to verify consistency

### 4. Finalize configuration

When stable:
- Update YAML config with working selectors
- Set `enabled: true`
- Set `environment: production`
- Move to production deployment

## Example: Amazon.com

```bash
# 1. Client provides requirements
cat clients/requirements/amazon_example.md

# 2. Generate files
python onboard_client.py clients/requirements/amazon_example.md

# 3. Test and debug (work with Claude Code)
python clients/amazon_com/test_amazon_com.py

# 4. When stable, enable in config
```

## Working with Claude Code

During debugging phase, tell Claude Code:
- "test the amazon client"
- "the search button selector is wrong, try finding it dynamically"
- "add error handling for the checkout step"
- "run it 3 times to verify stability"

Claude Code will iterate until the workflow is stable and repeatable.

## Reference Implementations

Use these as examples when building new clients:

### test_amazon_real.py - Basic Web Automation
**Good for:** Simple navigation, clicking, form filling

**Patterns:**
- Basic navigation with `browser.navigate()`
- Dynamic selector discovery with `browser.evaluate()`
- Simple clicking and form filling
- Screenshot capture at each step

### clients/[sandbar]/test_[sandbar].py - Production AML Client
**Good for:** Complex workflows with auth, decisions, state management

**Patterns:**
- **Auth caching**: Uses `storage_state` to skip login on repeat runs
- **Google SSO + 2FA**: Handles OAuth flow and push notifications
- **Keyboard shortcuts**: Uses `keyboard.press()` for fast UI interactions (y/n, g+c, Command+Enter)
- **Direct form setting**: Sets values with `browser.evaluate()` instead of typing
- **LLM decision making**: Reads page badges, generates reasoning and details
- **Skip processed items**: Checks for existing decisions before processing
- **Retry logic**: Loops through items until finding unprocessed ones
- **Full audit trail**: Screenshots + JSON metadata at every step

## Common Techniques

### When to use auth caching
- Client has slow login (OAuth, 2FA, etc)
- Testing requires many runs
- Session persists between runs
- **See:** Sandbar implementation (lines 42-46, 226-228)

### When to use keyboard shortcuts
- Client provides keyboard navigation (check docs or UI hints)
- Faster than waiting for clicks/DOM updates
- Especially useful for form submission (Command+Enter)
- **See:** Sandbar implementation (lines 636-772)

### When to set form values directly
- Typing is slow or unreliable
- Client expects full value instantly (no onChange events)
- Need to paste multi-line text
- **See:** Sandbar implementation (lines 703-713, 757-766)

### Dynamic selector discovery
- Always prefer over hardcoded selectors
- Use text content as fallback when ID/class unavailable
- Check `offsetParent !== null` to ensure visibility
- **See:** Both implementations use this pattern throughout
