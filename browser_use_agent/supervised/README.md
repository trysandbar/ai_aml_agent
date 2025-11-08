# Supervised Training App

Interactive workflow training for browser automation. Train workflows by pair-programming with an AI agent that asks for help when stuck.

## What This Does

**Training a workflow:**
1. Agent attempts your task
2. Monitors each step in real-time
3. Detects when stuck (loops, errors, no progress)
4. **Pauses and asks YOU**: "I'm stuck clicking this button. What should I do?"
5. You provide hint: "Click the 'Customers' link in the sidebar"
6. Agent incorporates hint and continues
7. Success → Saves learned workflow with all your guidance
8. Commit → Move to next site

## Quick Start

```bash
cd supervised

# Train a new workflow
python train.py \
  --task-file ../sandbar_simple.txt \
  --name sandbar_review

# Agent will pause when stuck and ask for help
# Type your hints, agent continues
# Workflow saved to workflows/sandbar_review.yml
```

## Usage

### Train New Workflow

```bash
# From task file
python train.py \
  --task-file ../sandbar_simple.txt \
  --name sandbar_customer_review

# Inline task
python train.py \
  --task "Go to Sandbar, click Customers, pick customer with alerts, check AI Summary" \
  --name sandbar_review

# The agent will run up to 5 training iterations
# Each iteration: run → detect stuck → pause → ask for hint → restart with hint
```

### Re-train Existing Workflow

```bash
# If workflow breaks (site changed)
python train.py --retrain workflows/sandbar_review.yml
```

## Interactive Training Flow

```
┌─────────────────────────────────────────────┐
│ Training Iteration 1/5                      │
│ Agent runs task...                          │
│ Gets stuck scrolling → pauses               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ ⏸️  PAUSED - Agent appears stuck            │
│ Reason: Scrolling 4 times without progress  │
│                                             │
│ Recent actions:                             │
│ 1. scroll                                   │
│ 2. scroll                                   │
│ 3. scroll                                   │
│ 4. scroll                                   │
│                                             │
│ 💡 What should I try instead?               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ You type hint:                              │
│ > Customer list visible. Click row with     │
│   alert badges                              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 💡 Got it! Restarting with your hint...    │
│                                             │
│ Training Iteration 2/5                      │
│ Agent runs with guidance...                 │
│ ✅ Task completed!                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 📝 Documenting successful workflow...      │
│    Captured 8 learning steps                │
│    With 1 user guidance hints               │
│ 💾 workflows/sandbar_review.yml             │
└─────────────────────────────────────────────┘
```

## Loop Detection

Automatically detects:
- **Repeated actions**: Same element clicked 3+ times
- **Error loops**: 3+ errors in last 5 steps
- **Scroll loops**: Scrolling 4+ times without progress

When detected → Agent pauses and asks for help

## Workflow Format

Learned workflows are saved as YAML:

```yaml
name: sandbar_customer_review
description: Review a customer with alerts on Sandbar
created_at: '2025-11-08T12:00:00'
last_trained: '2025-11-08T12:00:00'
success_count: 1
failure_count: 0
steps:
  - step_number: 1
    action: guidance
    description: 'User guidance: Click any customer row with alert badges'
    user_hint: Click any customer row with alert badges
  - step_number: 2
    action: click
    description: 'Step 2: click'
  - step_number: 3
    action: completed
    description: 'Task completed: Customer: John Doe, AI Summary: Review, Decision: MATCH'
```

## Tips for Effective Training

1. **Be specific**: "Click 'Customers' link" > "Go to customers"
2. **Provide context**: "Look in the left sidebar for navigation links"
3. **Describe UI**: "The customer list is already showing, don't scroll"
4. **Type 'quit' to stop**: Saves partial learning

## Files

- `train.py` - Main training script
- `supervisor.py` - SupervisedAgent class with lifecycle hooks
- `loop_detector.py` - Loop detection logic
- `workflow_model.py` - Data models (WorkflowStep, LearnedWorkflow)
- `workflows/` - Saved learned workflows

## Development Flow

```bash
# 1. Train workflow
python train.py --task-file ../acme.txt --name acme_review

# 2. Test replay (use runner app)
cd ../runner
python run.py --workflow ../supervised/workflows/acme_review.yml

# 3. Works? Commit!
git add ../supervised/workflows/acme_review.yml
git commit -m "Add trained ACME review workflow"

# 4. Move to next site
```

## Architecture

```
SupervisedAgent (supervisor.py)
├── Uses browser-use Agent with lifecycle hooks
├── on_step_end: Monitor each step in real-time
├── LoopDetector: Analyze action patterns
├── Pause when stuck → Ask user
├── Incorporate hints → Continue
└── Document success → Save workflow

LoopDetector (loop_detector.py)
├── Track action history
├── Detect repeated actions
├── Detect error loops
└── Detect scroll loops

WorkflowLearner (supervisor.py)
├── Extract successful steps from history
├── Include user guidance hints
├── Save to YAML
└── Load for replay
```

## Next Steps

After training, use the **runner app** to execute workflows:

```bash
cd ../runner
python run.py --workflow ../supervised/workflows/sandbar_review.yml
```

See `../runner/README.md` for execution details.
