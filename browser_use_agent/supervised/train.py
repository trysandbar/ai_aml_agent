#!/usr/bin/env python3
"""
Interactive Workflow Training

Trains browser automation workflows by:
1. Running agent in small chunks
2. Detecting when stuck
3. Asking user for guidance
4. Documenting successful patterns
5. Saving learned workflows for replay

Usage:
    # Train a new workflow
    python train_workflow.py --task "Review customer on Sandbar" --name sandbar_review

    # Replay a saved workflow
    python train_workflow.py --replay workflows/sandbar_review.yml
"""

#!/usr/bin/env python3

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import argparse

from agent import AgentConfig
from supervised.supervisor import SupervisedAgent


async def train_new_workflow(args):
    """Train a new workflow interactively"""
    print(f"\n{'='*70}")
    print(f"🎓 INTERACTIVE WORKFLOW TRAINING")
    print(f"{'='*70}\n")

    # Load config
    config = AgentConfig.from_env()

    # Create supervised agent in training mode
    agent = SupervisedAgent(config, training_mode=True)

    # Load task from file or use provided task
    if args.task_file:
        task = Path(args.task_file).read_text().strip()
        print(f"📋 Task loaded from: {args.task_file}")
    else:
        task = args.task

    print(f"\n📝 Task: {task}\n")
    print(f"{'='*70}")
    print("How this works:")
    print("1. I'll try the task in small chunks (8 steps at a time)")
    print("2. If I get stuck, I'll pause and ask for your help")
    print("3. You give me a hint, and I'll try again with your guidance")
    print("4. When successful, I'll save the workflow for replay")
    print(f"{'='*70}\n")

    input("Press ENTER to start training...")

    # Train the workflow
    workflow = await agent.train_workflow(task, args.name)

    # Save workflow
    output_dir = Path("browser_use_agent/workflows")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.name}.yml"

    agent.save_workflow(workflow, output_path)

    print(f"\n{'='*70}")
    print(f"✅ Training Complete!")
    print(f"{'='*70}")
    print(f"Workflow: {workflow.name}")
    print(f"Steps learned: {len(workflow.steps)}")
    print(f"Saved to: {output_path}")
    print(f"\nYou can now replay this workflow with:")
    print(f"  python train_workflow.py --replay {output_path}")
    print(f"{'='*70}\n")

    return 0


async def replay_workflow(args):
    """Replay a saved workflow"""
    workflow_path = Path(args.replay)

    if not workflow_path.exists():
        print(f"❌ Workflow not found: {workflow_path}")
        return 1

    print(f"\n{'='*70}")
    print(f"▶️  REPLAY MODE")
    print(f"{'='*70}\n")

    # Load config
    config = AgentConfig.from_env()

    # Create supervised agent
    agent = SupervisedAgent(config, training_mode=False)

    # Load workflow
    workflow = agent.load_workflow(workflow_path)

    print(f"Workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Steps: {len(workflow.steps)}")
    print(f"Success history: {workflow.success_count} successes, {workflow.failure_count} failures")
    print(f"\n{'='*70}\n")

    input("Press ENTER to execute workflow...")

    # Execute workflow
    result = await agent.replay_workflow(workflow)

    # Save updated stats
    agent.save_workflow(workflow, workflow_path)

    if result['status'] == 'completed':
        print(f"\n✅ Workflow executed successfully!")
        return 0
    else:
        print(f"\n⚠️  Workflow execution had issues.")
        print(f"\nYou can re-train this workflow with:")
        print(f"  python train_workflow.py --retrain {workflow_path}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Interactive workflow training for browser automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train a new workflow with inline task
  python train_workflow.py \\
    --task "Go to Sandbar, review a customer with alerts" \\
    --name sandbar_review

  # Train using task from file
  python train_workflow.py \\
    --task-file sandbar_simple.txt \\
    --name sandbar_simple

  # Replay a saved workflow
  python train_workflow.py --replay workflows/sandbar_review.yml

  # Re-train an existing workflow that broke
  python train_workflow.py --retrain workflows/sandbar_review.yml

Training Flow:
  1. Agent tries task → gets stuck
  2. Agent: "I'm stuck, what should I do?"
  3. You: "Click the Customers link in the sidebar"
  4. Agent: "Got it!" → continues with hint
  5. Success → saves workflow
  6. Commit → move to next site
        """
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--task",
        help="Natural language task to train (inline)"
    )
    mode_group.add_argument(
        "--task-file",
        help="Path to file containing task description"
    )
    mode_group.add_argument(
        "--replay",
        help="Path to saved workflow YAML to replay"
    )
    mode_group.add_argument(
        "--retrain",
        help="Path to saved workflow YAML to re-train"
    )

    # Training options
    parser.add_argument(
        "--name",
        help="Name for the workflow (required for training)"
    )

    args = parser.parse_args()

    # Validate args
    if (args.task or args.task_file) and not args.name:
        parser.error("--name is required when training a new workflow")

    # Run appropriate mode
    if args.replay:
        exit_code = asyncio.run(replay_workflow(args))
    elif args.retrain:
        # Re-training is same as training but loads existing workflow
        args.replay = args.retrain
        workflow_path = Path(args.retrain)
        # Extract name from filename
        args.name = workflow_path.stem
        # Load existing task
        agent_config = AgentConfig.from_env()
        temp_agent = SupervisedAgent(agent_config, training_mode=True)
        workflow = temp_agent.load_workflow(workflow_path)
        args.task = workflow.description
        exit_code = asyncio.run(train_new_workflow(args))
    else:
        exit_code = asyncio.run(train_new_workflow(args))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
