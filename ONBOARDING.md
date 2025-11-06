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
