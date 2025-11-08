# Workflow Runner App

Executes trained workflows created by the supervised training app. Simple, production-ready runner for repeatable automation.

## What This Does

Takes a trained workflow (YAML file) and executes it:
- Loads workflow with learned steps + user guidance
- Runs autonomously (no interaction needed)
- Tracks success/failure stats
- Returns exit code 0 (success) or 1 (failure)

## Quick Start

```bash
cd runner

# Run a trained workflow
python run.py --workflow ../supervised/workflows/sandbar_review.yml

# Success!
# ✅ Workflow executed successfully!
```

## Usage

### Run Trained Workflow

```bash
python run.py --workflow ../supervised/workflows/sandbar_customer_review.yml
```

### With Custom Config

```bash
# Use different API key
TOGETHER_API_KEY=xxx python run.py --workflow ../supervised/workflows/sandbar_review.yml

# Use different model
TOGETHER_MODEL=moonshotai/Kimi-K2-Instruct-0905 python run.py --workflow ../supervised/workflows/sandbar_review.yml
```

## Exit Codes

- **0**: Workflow executed successfully
- **1**: Workflow failed or had errors

Use in scripts:

```bash
if python run.py --workflow ../supervised/workflows/sandbar_review.yml; then
    echo "Success!"
else
    echo "Failed - re-training needed"
    cd ../supervised
    python train.py --retrain workflows/sandbar_review.yml
fi
```

## Output

```
======================================================================
▶️  EXECUTING TRAINED WORKFLOW
======================================================================

Workflow: sandbar_customer_review
Description: Review a customer with alerts on Sandbar
Steps: 8
Success history: 5 / 6

======================================================================

[Agent executes workflow...]

======================================================================
✅ Workflow executed successfully!
======================================================================
```

## When Workflows Fail

If a workflow fails (site changed, new UI):

```bash
# Re-train the workflow
cd ../supervised
python train.py --retrain workflows/sandbar_review.yml

# You'll pair-train again to update the workflow
# Then test with runner:
cd ../runner
python run.py --workflow ../supervised/workflows/sandbar_review.yml
```

## Production Integration

### CI/CD Pipeline

```yaml
# .github/workflows/run-workflows.yml
name: Run Automation Workflows

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  run-workflows:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          cd browser_use_agent
          pip install -r requirements.txt

      - name: Run Sandbar workflow
        env:
          TOGETHER_API_KEY: ${{ secrets.TOGETHER_API_KEY }}
        run: |
          cd browser_use_agent/runner
          python run.py --workflow ../supervised/workflows/sandbar_review.yml

      - name: Notify on failure
        if: failure()
        run: |
          echo "Workflow failed - may need re-training"
```

### Cron Job

```bash
# /etc/cron.d/automation-workflows
0 */6 * * * cd /app/browser_use_agent/runner && python run.py --workflow ../supervised/workflows/sandbar_review.yml >> /var/log/workflows.log 2>&1
```

### Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY browser_use_agent/ /app/browser_use_agent/

RUN cd /app/browser_use_agent && pip install -r requirements.txt

# Run workflows
CMD ["python", "/app/browser_use_agent/runner/run.py", "--workflow", "/app/browser_use_agent/supervised/workflows/sandbar_review.yml"]
```

## Monitoring

Track workflow health:

```bash
# Parse exit codes
python run.py --workflow ../supervised/workflows/sandbar_review.yml
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    # Log success
    echo "$(date) - sandbar_review: SUCCESS" >> /var/log/workflow-health.log
else
    # Alert on failure
    echo "$(date) - sandbar_review: FAILED" >> /var/log/workflow-health.log
    # Send alert (Slack, PagerDuty, etc.)
fi
```

## Files

- `run.py` - Main execution script

## Workflow Stats

Each execution updates the workflow file:

```yaml
success_count: 6  # Incremented on success
failure_count: 1  # Incremented on failure
```

Track reliability over time.

## Development Flow

```bash
# 1. Train workflow (supervised app)
cd ../supervised
python train.py --task-file ../acme.txt --name acme_review

# 2. Test execution (runner app)
cd ../runner
python run.py --workflow ../supervised/workflows/acme_review.yml

# 3. Works? Production ready!
# Add to CI/CD or cron
```

## Comparison: Training vs Running

| Feature | Supervised Training | Runner |
|---------|-------------------|--------|
| **Mode** | Interactive | Autonomous |
| **User interaction** | Pauses for help | None |
| **Loop detection** | Yes | No |
| **Purpose** | Learn workflow | Execute workflow |
| **Output** | YAML workflow | Exit code |
| **When to use** | First time, broken workflow | Production, automation |

## Next Steps

**Workflow broken?** Re-train with supervised app:

```bash
cd ../supervised
python train.py --retrain workflows/sandbar_review.yml
```

**New site?** Train new workflow:

```bash
cd ../supervised
python train.py --task-file ../newsite.txt --name newsite_workflow
```

See `../supervised/README.md` for training details.
