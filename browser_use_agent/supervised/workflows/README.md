# Interactive Workflow Training

This directory contains learned workflows that can be replayed or re-trained.

## Training Flow

1. **Agent tries task** → monitors each step in real-time
2. **Gets stuck** (repeated actions, errors, no progress)
3. **Pauses and asks you**: "I'm stuck clicking this button repeatedly. What should I do?"
4. **You provide hint**: "Look for a link with text 'Customers' in the sidebar and click it"
5. **Agent continues** with your guidance injected into its task
6. **Success** → Agent documents all steps and user hints
7. **Saves workflow** to YAML file for replay
8. **You commit** → move to next site

## Usage

### Train a New Workflow

```bash
# From task description file
python train_workflow.py \
  --task-file sandbar_simple.txt \
  --name sandbar_customer_review

# Inline task
python train_workflow.py \
  --task "Go to Sandbar and review a customer with alerts" \
  --name sandbar_review
```

### Replay a Saved Workflow

```bash
python train_workflow.py --replay workflows/sandbar_customer_review.yml
```

### Re-train if Workflow Breaks

```bash
python train_workflow.py --retrain workflows/sandbar_customer_review.yml
```

## Workflow Format

Learned workflows are saved as YAML:

```yaml
name: sandbar_customer_review
description: Review a customer with alerts on Sandbar
created_at: '2025-11-07T21:30:00'
last_trained: '2025-11-07T21:30:00'
success_count: 1
failure_count: 0
steps:
  - step_number: 1
    action: guidance
    description: 'User guidance: Click the Customers link in the sidebar'
    user_hint: Click the Customers link in the sidebar
  - step_number: 2
    action: click
    description: 'Step 2: click'
    selector: null
  - step_number: 3
    action: completed
    description: 'Task completed: Customer: John Doe, AI Summary: Review, Decision: MATCH'
```

## Loop Detection

The system automatically detects:
- **Repeated actions**: Same action 3+ times (e.g., clicking same button)
- **Error loops**: 3+ errors in last 5 steps
- **Scroll loops**: Scrolling 4+ times without progress

When detected, agent pauses and asks for help.

## Tips for Effective Training

1. **Be specific in hints**: "Click the 'Customers' link" vs "Go to customers"
2. **Provide UI details**: "Look for the sidebar on the left with navigation links"
3. **Type 'quit' to stop**: Training cancelled, partial learning saved
4. **Iterate**: Re-train if site changes or workflow breaks

## Development Workflow

```bash
# 1. Train workflow for new site
python train_workflow.py --task-file acme.txt --name acme_review

# 2. Test replay
python train_workflow.py --replay workflows/acme_review.yml

# 3. Works? Commit!
git add workflows/acme_review.yml
git commit -m "Add trained workflow for ACME review"

# 4. Move to next site
```

## Architecture

- `SupervisedAgent`: Wraps browser-use Agent with monitoring
- `LoopDetector`: Analyzes action history for stuck patterns
- `WorkflowLearner`: Documents successful steps + user hints
- `Lifecycle Hooks`: Real-time step monitoring via `on_step_end`

## Lifecycle Hook Integration

Uses browser-use's `on_step_end` hook to monitor each step:

```python
async def on_step_end(agent):
    # Check for loops
    # Pause if stuck
    # Ask user for help
    # Document learning

await agent.run(on_step_end=on_step_end)
```

This enables real-time intervention without chunked execution.
